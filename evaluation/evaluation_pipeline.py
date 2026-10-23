# evaluation_pipeline.py
import pandas as pd
import json
from datetime import datetime
from langchain_openrouter import ChatOpenRouter
from langchain_core.messages import HumanMessage, SystemMessage
from evaluator import compute_rouge, compute_bleu4, compute_token_f1
from llm_judge import llm_judge
from evaluation_data import CLINICAL_EVALUATION_DATA
import os
from dotenv import load_dotenv
import time

load_dotenv()


from evaluation_data import CLINICAL_EVALUATION_DATA


TEST_QUESTIONS = CLINICAL_EVALUATION_DATA[:7]

class EvaluationPipeline:
    def __init__(self, models=["gpt-4o-mini", "gpt-4o"]):
        self.models = models
        self.results = []
        
    def get_llm(self, model_name):
        return ChatOpenRouter(
            openrouter_api_key=os.environ.get("OPENROUTER_API_KEY", ""),
            model=model_name,
            temperature=0,
            max_tokens=100
        )
    
    def run_evaluation(self):
        for model_name in self.models:
            print(f"\n{'='*60}\nEvaluating {model_name}\n{'='*60}")
            llm = self.get_llm(model_name)
            
            for item in CLINICAL_EVALUATION_DATA:
                question = item["question"]
                reference = item["reference"]
                channel = item["channel"]
                feature = item["feature"]
                
                response = llm.invoke([
                    SystemMessage(content="You are an expert AfyaPlus clinical service agent."),
                    HumanMessage(content=question)
                ])
                hypothesis = response.content

                time.sleep(2)  # Wait 2 seconds between requests
                
                rouge_scores = compute_rouge(reference, hypothesis)
                bleu_4 = compute_bleu4(reference, hypothesis)
                token_f1 = compute_token_f1(reference, hypothesis)
                
                judge_scores = llm_judge(question, reference, hypothesis)
                
                row = {
                    "question": question[:50] + "...",
                    "channel": channel,
                    "feature": feature,
                    "model": model_name,
                    "bleu_4": round(bleu_4, 4),
                    "rouge_l": rouge_scores.get("rougeL", 0),
                    "token_f1": token_f1,
                    "correctness": judge_scores.get("correctness", 0),
                    "groundedness": judge_scores.get("groundedness", 0),
                    "relevance": judge_scores.get("relevance", 0),
                    "helpfulness": judge_scores.get("helpfulness", 0),
                    "judge_overall": judge_scores.get("overall", 0),
                    "reasoning": judge_scores.get("reasoning", "")
                }
                self.results.append(row)
                
                print(f"\nQ: {question[:60]}...")
                print(f"ROUGE-L: {row['rouge_l']:.3f} | BLEU-4: {row['bleu_4']:.3f}")
                print(f"Judge Overall: {row['judge_overall']}/5")
                print("-" * 40)
        
        return pd.DataFrame(self.results)
    
    def generate_summary(self, df):
        summary = df.groupby("model").agg(
            avg_rouge_l=("rouge_l", "mean"),
            avg_bleu_4=("bleu_4", "mean"),
            avg_token_f1=("token_f1", "mean"),
            avg_judge=("judge_overall", "mean"),
            avg_correctness=("correctness", "mean"),
            avg_groundedness=("groundedness", "mean"),
            avg_relevance=("relevance", "mean"),
            avg_helpfulness=("helpfulness", "mean"),
        ).round(4)
        return summary
    
    def quality_gate_assessment(self, df):
        THRESHOLDS = {
            "rouge_l_min": 0.25,
            "judge_overall_min": 3.0,
            "groundedness_min": 2.5,
            "correctness_min": 3.0
        }
        
        model_passes = {}
        model_gates = {}
        
        for model in df["model"].unique():
            model_data = df[df["model"] == model]
            gate_details = {}
            passes = []
            
            metrics = {
                "rouge_l": (model_data["rouge_l"].mean(), THRESHOLDS["rouge_l_min"]),
                "judge_overall": (model_data["judge_overall"].mean(), THRESHOLDS["judge_overall_min"]),
                "groundedness": (model_data["groundedness"].mean(), THRESHOLDS["groundedness_min"]),
                "correctness": (model_data["correctness"].mean(), THRESHOLDS["correctness_min"])
            }
            
            for metric_name, (value, threshold) in metrics.items():
                status = "PASS" if value >= threshold else "FAIL"
                passes.append(value >= threshold)
                gate_details[metric_name] = {
                    "value": round(value, 3),
                    "threshold": threshold,
                    "status": status
                }
            
            model_passes[model] = all(passes)
            model_gates[model] = gate_details
        
        return model_passes, model_gates
    
    def save_results(self):
        df = pd.DataFrame(self.results)
        df.to_csv("full_evaluation_results.csv", index=False)
        
        summary = self.generate_summary(df)
        summary.to_csv("model_comparison_summary.csv")
        
        passes, gates = self.quality_gate_assessment(df)
        with open("quality_gate_report.json", "w") as f:
            json.dump({
                "model_passes": passes,
                "model_gates": gates,
                "timestamp": datetime.utcnow().isoformat()
            }, f, indent=2)
        
        print("\n" + "="*60)
        print("QUALITY GATE ASSESSMENT")
        print("="*60)
        for model, passes_flag in passes.items():
            status = "PASS" if passes_flag else "FAIL"
            print(f"{model:15} {status}")
            for gate, details in gates[model].items():
                print(f"  {gate:15} {details['status']:5} ({details['value']:.3f} ≥ {details['threshold']})")
        
        return df, summary

if __name__ == "__main__":
    pipeline = EvaluationPipeline(models=["gpt-4o-mini", "gpt-4o"])
    results_df = pipeline.run_evaluation()
    df, summary = pipeline.save_results()
    
    print("\n" + "="*60)
    print("MODEL COMPARISON SUMMARY")
    print("="*60)
    print(summary.to_string())