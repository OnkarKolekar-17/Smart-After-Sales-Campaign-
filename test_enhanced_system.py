"""
Test the enhanced multi-campaign system with real email
"""
import subprocess
import sys
import os

def main():
    print("🚀 TESTING ENHANCED SMART CAMPAIGN SYSTEM")
    print("=" * 60)
    print()
    print("✅ System Enhancements:")
    print("   • Vehicle Lifecycle Agent added")
    print("   • Multiple campaign types (weather, holiday, lifecycle)")
    print("   • Targeted email sending to specific segments")  
    print("   • ALL relevant customers included (no 2-person limit)")
    print("   • Real email testing with: onkar.kolekar23@vit.edu")
    print()
    
    # Test 1: Check if Brevo is now working
    print("📧 TEST 1: Brevo Email Service Check")
    print("-" * 40)
    
    try:
        result = subprocess.run([
            sys.executable, "test_real_email.py"
        ], cwd=os.getcwd(), capture_output=True, text=True)
        
        if "SUCCESS" in result.stdout:
            print("✅ Brevo email service is working!")
            print("🎯 You should receive a test email in your inbox")
        else:
            print("⚠️  Brevo may still need IP whitelisting")
            print("   Visit: https://app.brevo.com/security/authorised_ips")
            print("   Add IP: 124.66.174.160")
        
    except Exception as e:
        print(f"❌ Error testing Brevo: {e}")
    
    print()
    print("🔄 TEST 2: Enhanced Campaign System")
    print("-" * 40)
    print("Running comprehensive multi-agent campaign workflow...")
    print("This will generate multiple campaign types and send targeted emails.")
    print()
    
    # Test 2: Run the enhanced campaign system
    try:
        result = subprocess.run([
            sys.executable, "main.py", 
            "--mode", "single", 
            "--location", "Mumbai", 
            "--trigger", "weather"
        ], cwd=os.getcwd(), capture_output=True, text=True)
        
        print("📊 CAMPAIGN RESULTS:")
        print("-" * 20)
        
        if "success" in result.stdout.lower():
            # Extract key metrics from output
            lines = result.stdout.split('\n')
            for line in lines:
                if any(word in line.lower() for word in ['targeted', 'campaigns', 'sent', 'weather', 'holiday']):
                    print(f"   {line.strip()}")
            
            print()
            print("🎯 WHAT TO EXPECT:")
            print("   📧 Check onkar.kolekar23@vit.edu for campaign emails")
            print("   🌟 You should receive multiple targeted campaigns:")
            print("      • Weather-based monsoon care campaign")
            print("      • Ganesh Chaturthi holiday campaign")
            print("      • Vehicle lifecycle-based campaigns")
            print("   📊 Each email will be personalized based on customer data")
            
        else:
            print("❌ Campaign execution issues detected")
            print("Check the logs above for details")
            
    except Exception as e:
        print(f"❌ Error running campaign: {e}")
    
    print()
    print("🔍 VERIFICATION STEPS:")
    print("=" * 60)
    print("1. Check your email inbox: onkar.kolekar23@vit.edu")
    print("2. Look for multiple campaign emails with different subjects")
    print("3. Verify personalized content in each email")
    print("4. Check Brevo dashboard: https://app.brevo.com/email/transactional")
    print("5. Confirm all Mumbai customers received relevant campaigns")
    print()
    print("🎉 If you receive multiple personalized emails, your Smart Campaign System")
    print("   is working perfectly with comprehensive targeting and multi-campaign support!")

if __name__ == "__main__":
    main()
