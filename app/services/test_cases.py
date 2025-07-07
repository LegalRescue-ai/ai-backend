# test_cases.py -  test cases for drift detection

REGRESSION_TEST_CASES = [
    # Criminal Law Cases
    {
        "text": "I was arrested for marijuana possession last night",
        "expected_category": "Criminal Law",
        "expected_subcategory": "Drug Crimes"
    },
    {
        "text": "Got a DUI and need help with my court case",
        "expected_category": "Criminal Law", 
        "expected_subcategory": "Drunk Driving/DUI/DWI"
    },
    {
        "text": "Charged with embezzlement at my company",
        "expected_category": "Criminal Law",
        "expected_subcategory": "White Collar Crime"
    },
    {
        "text": "Arrested for assault at a bar last weekend",
        "expected_category": "Criminal Law",
        "expected_subcategory": "General Criminal Defense"
    },
    
    # Family Law Cases  
    {
        "text": "My wife and I are getting divorced and need to split our business assets",
        "expected_category": "Family Law",
        "expected_subcategory": "Divorce"
    },
    {
        "text": "My ex won't let me see my kids and I want custody",
        "expected_category": "Family Law",
        "expected_subcategory": "Child Custody & Visitation"
    },
    {
        "text": "Need help getting child support from my ex-husband",
        "expected_category": "Family Law",
        "expected_subcategory": "Child Support"
    },
    {
        "text": "My spouse and I are divorcing and we own a restaurant together",
        "expected_category": "Family Law",
        "expected_subcategory": "Divorce"  # Should be Family Law, NOT Business Law
    },
    
    # Employment Law Cases
    {
        "text": "I was fired for reporting safety violations at work",
        "expected_category": "Employment Law",
        "expected_subcategory": "Wrongful Termination"
    },
    {
        "text": "I think I was passed over for promotion because of my age",
        "expected_category": "Employment Law",
        "expected_subcategory": "Employment Discrimination"
    },
    {
        "text": "My boss won't pay me overtime even though I work 60 hours a week",
        "expected_category": "Employment Law",
        "expected_subcategory": "Wages and Overtime Pay"
    },
    {
        "text": "Sexual harassment by my supervisor at work",
        "expected_category": "Employment Law",
        "expected_subcategory": "Sexual Harassment"
    },
    
    # Personal Injury Cases
    {
        "text": "Hit by a drunk driver and suffered serious injuries",
        "expected_category": "Personal Injury Law",
        "expected_subcategory": "Automobile Accidents"
    },
    {
        "text": "Doctor misdiagnosed my condition and it got worse",
        "expected_category": "Personal Injury Law",
        "expected_subcategory": "Medical Malpractice"
    },
    {
        "text": "Slipped and fell at the grocery store and broke my hip",
        "expected_category": "Personal Injury Law",
        "expected_subcategory": "Personal Injury (General)"
    },
    {
        "text": "Company sold me a defective product that injured me",
        "expected_category": "Personal Injury Law", 
        "expected_subcategory": "Defective Products"  # Physical injury = Personal Injury
    },
    
    # Product Liability Cases
    {
        "text": "My XYZ brand water filter contaminated my water and made me sick",
        "expected_category": "Product & Services Liability Law",
        "expected_subcategory": "Defective Products"
    },
    {
        "text": "My lawyer failed to file important documents and I lost my case",
        "expected_category": "Product & Services Liability Law",
        "expected_subcategory": "Attorney Malpractice"
    },
    {
        "text": "Company sold me a defective refrigerator that doesn't work",
        "expected_category": "Product & Services Liability Law",
        "expected_subcategory": "Defective Products"
    },
    {
        "text": "Water filter company sold me a filter that doesn't work properly",
        "expected_category": "Product & Services Liability Law",
        "expected_subcategory": "Defective Products"  # No injury = Product Liability
    },
    
    # Business Law Cases
    {
        "text": "My business partner stole our customer list and started competing",
        "expected_category": "Business/Corporate Law",
        "expected_subcategory": "Business Disputes"
    },
    {
        "text": "Vendor didn't deliver goods as specified in our contract",
        "expected_category": "Business/Corporate Law",
        "expected_subcategory": "Breach of Contract"
    },
    {
        "text": "Need help forming an LLC for my new business",
        "expected_category": "Business/Corporate Law",
        "expected_subcategory": "Corporations, LLCs, Partnerships, etc."
    },
    {
        "text": "My business partner stole our company's customer list and trade secrets",
        "expected_category": "Business/Corporate Law",
        "expected_subcategory": "Business Disputes"
    },
    
    # Real Estate Cases
    {
        "text": "Seller didn't disclose major problems with the house I bought",
        "expected_category": "Real Estate Law",
        "expected_subcategory": "Purchase and Sale of Residence"
    },
    {
        "text": "Bank is foreclosing on my house and I need help",
        "expected_category": "Real Estate Law",
        "expected_subcategory": "Foreclosures"
    },
    {
        "text": "Having problems with my mortgage company",
        "expected_category": "Real Estate Law",
        "expected_subcategory": "Mortgages"
    },
    
    # Landlord/Tenant Cases
    {
        "text": "Landlord won't fix the broken heating system",
        "expected_category": "Landlord/Tenant Law",
        "expected_subcategory": "General cases"
    },
    {
        "text": "Got an eviction notice but don't think it's legal",
        "expected_category": "Landlord/Tenant Law", 
        "expected_subcategory": "General cases"
    },
    
    # Immigration Cases
    {
        "text": "Facing deportation and need immigration lawyer",
        "expected_category": "Immigration Law",
        "expected_subcategory": "Deportation"
    },
    {
        "text": "Green card application was denied",
        "expected_category": "Immigration Law",
        "expected_subcategory": "Permanent Visas or Green Cards"
    },
    {
        "text": "Need help with citizenship application",
        "expected_category": "Immigration Law",
        "expected_subcategory": "Citizenship"
    },
    
    # Bankruptcy Cases
    {
        "text": "Can't pay my debts and considering bankruptcy",
        "expected_category": "Bankruptcy, Finances, & Tax Law",
        "expected_subcategory": "Consumer Bankruptcy"
    },
    {
        "text": "Debt collectors are harassing me at work",
        "expected_category": "Bankruptcy, Finances, & Tax Law",
        "expected_subcategory": "Collections"
    },
    {
        "text": "IRS is auditing me and I need help",
        "expected_category": "Bankruptcy, Finances, & Tax Law",
        "expected_subcategory": "Income Tax"
    },
    
    # Government/Administrative Cases
    {
        "text": "My disability benefits were denied by Social Security",
        "expected_category": "Government & Administrative Law",
        "expected_subcategory": "Social Security – Disability"
    },
    {
        "text": "VA denied my benefits claim",
        "expected_category": "Government & Administrative Law",
        "expected_subcategory": "Veterans Benefits"
    },
    
    # Intellectual Property Cases
    {
        "text": "Someone stole my invention and is selling it",
        "expected_category": "Intellectual Property Law",
        "expected_subcategory": "Patents"
    },
    {
        "text": "Company is using my copyrighted material without permission",
        "expected_category": "Intellectual Property Law",
        "expected_subcategory": "Copyright"
    },
    {
        "text": "Another business is using my trademark",
        "expected_category": "Intellectual Property Law",
        "expected_subcategory": "Trademarks"
    },
    
    # Wills/Estates Cases
    {
        "text": "Need help writing a will and estate planning",
        "expected_category": "Wills, Trusts, & Estates Law",
        "expected_subcategory": "Estate Planning"
    },
    {
        "text": "Family fighting over inheritance after dad died",
        "expected_category": "Wills, Trusts, & Estates Law",
        "expected_subcategory": "Contested Wills or Probate"
    },
    
    # Edge Cases - These often get misclassified
    {
        "text": "Arrested for having cocaine at a party",
        "expected_category": "Criminal Law",
        "expected_subcategory": "Drug Crimes"  # Should be Drug Crimes, NOT General Criminal
    }
]

def run_quick_test():
    """Quick test function to validate accuracy"""
    from .case_analyzer import CaseAnalyzer
    import os
    
    # Initialize analyzer
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment variables")
        return
    
    analyzer = CaseAnalyzer(api_key)
    
    # Run a subset of tests for quick validation
    quick_test_cases = REGRESSION_TEST_CASES[:10]  # First 10 cases
    
    print(f"🧪 Running quick test with {len(quick_test_cases)} cases...")
    
    results = analyzer.run_regression_test(quick_test_cases)
    
    return results

def run_full_regression_test():
    """Run full regression test with all cases"""
    from .case_analyzer import CaseAnalyzer
    import os
    import json
    from datetime import datetime
    
    # Initialize analyzer
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment variables")
        return
    
    analyzer = CaseAnalyzer(api_key)
    
    # Run full regression test
    results = analyzer.run_regression_test(REGRESSION_TEST_CASES)
    
    # Save results for monitoring
    timestamp = results["timestamp"].replace(":", "-").replace(".", "-")
    filename = f"regression_test_results_{timestamp}.json"
    
    # Create logs directory if it doesn't exist
    import os
    os.makedirs("logs", exist_ok=True)
    
    with open(f"logs/{filename}", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"📊 Results saved to logs/{filename}")
    
    # Alert if accuracy drops below threshold
    if results["accuracy"] < 85:
        print("🚨 ALERT: Accuracy below 85% - possible model drift!")
        send_drift_alert(results)
    
    return results

def send_drift_alert(results):
    """Send alert when model drift is detected"""
    alert_message = f"""
    🚨 MODEL DRIFT ALERT 🚨
    
    Accuracy dropped to {results['accuracy']:.1f}%
    Expected: ≥85%
    
    System Version: {results['system_version']}
    Prompt Version: {results['prompt_version']}
    
    Failed Tests: {len([r for r in results['results'] if r['status'] != 'pass'])}
    Total Tests: {results['total_tests']}
    
    Review needed immediately.
    """
    
    print(alert_message)
    # In production: send to Slack, email, or monitoring dashboard

if __name__ == "__main__":
    # Run quick test when executed directly
    run_quick_test()