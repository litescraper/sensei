#!/usr/bin/env python3
"""
Quick demo script to showcase the Agents as a Loop and Judge mechanism.
"""
import os
import sys
from dotenv import load_dotenv
from src.main import Sensei
from src.config import ResearchDomain

# Load environment variables
load_dotenv()

def main():
    print("=" * 80)
    print("SENSEI - Autonomous Research Scientist Demo")
    print("Agents as a Loop and Judge Mechanism")
    print("=" * 80)
    print()
    
    # Check for required API keys
    required_keys = ["GOOGLE_API_KEY"]
    missing_keys = [key for key in required_keys if not os.getenv(key)]
    
    if missing_keys:
        print(f"⚠️  Missing API keys: {', '.join(missing_keys)}")
        print("Please set them in your .env file")
        return
    
    print("Initializing Sensei...")
    print()
    
    # Initialize with a quick domain and fewer papers for demo
    scientist = Sensei(
        domain=ResearchDomain.AI_SAFETY,
        provider="google",
        model_name="gemini-2.0-flash-exp",
        max_papers_to_analyze=5,  # Fewer papers for faster demo
        max_idea_generation_attempts=2,  # Fewer attempts for demo
        target_conference="ICML"
    )
    
    print("Starting research pipeline...")
    print("This will demonstrate:")
    print("  1. Generator creates initial idea")
    print("  2. Judge evaluates and provides feedback")
    print("  3. Refiner improves idea based on feedback")
    print("  4. Loop continues until idea passes or max iterations")
    print()
    print("-" * 80)
    print()
    
    try:
        # Run the pipeline
        report_path = scientist.run(output_dir="reports")
        
        if report_path:
            print()
            print("=" * 80)
            print("✅ DEMO COMPLETE!")
            print("=" * 80)
            print()
            print(f"Report saved to: {report_path}")
            print()
            print("The Agents as a Loop and Judge mechanism:")
            print("  ✓ Generator created initial idea")
            print("  ✓ Judge evaluated and provided feedback")
            print("  ✓ Refiner improved the idea iteratively")
            print("  ✓ Best idea was selected and reported")
            print()
        else:
            print()
            print("⚠️  Pipeline completed but no report was generated.")
            print("Check logs above for details.")
            
    except KeyboardInterrupt:
        print()
        print("\n⚠️  Demo interrupted by user")
        sys.exit(1)
    except Exception as e:
        print()
        print(f"❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

