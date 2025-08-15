"""
Test Brevo email sending functionality independently
"""
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from config.settings import settings

def test_brevo_connection():
    """Test if Brevo API is working and can send a test email"""
    
    print("🔧 Testing Brevo API Connection...")
    print(f"📧 Sender: {settings.brevo.sender_name} <{settings.brevo.sender_email}>")
    print(f"🔑 API Key: {settings.brevo.api_key[:8]}...")
    print()
    
    try:
        # Initialize Brevo API client
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = settings.brevo.api_key
        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
            sib_api_v3_sdk.ApiClient(configuration)
        )
        
        # Create test email
        test_email = sib_api_v3_sdk.SendSmtpEmail(
            to=[sib_api_v3_sdk.SendSmtpEmailTo(
                email="onkar.kolekar23@vit.edu",  # Your email
                name="Test Recipient"
            )],
            sender=sib_api_v3_sdk.SendSmtpEmailSender(
                name=settings.brevo.sender_name,
                email=settings.brevo.sender_email
            ),
            subject="🧪 Smart Campaign System - Test Email",
            html_content="""
            <h2>✅ Brevo Integration Test Successful!</h2>
            <p>If you're reading this, your Smart After-Sales Campaign system is successfully connected to Brevo!</p>
            <p><strong>Test Details:</strong></p>
            <ul>
                <li>Date: August 15, 2025</li>
                <li>System: Smart After-Sales Campaign</li>
                <li>Status: Email delivery working</li>
            </ul>
            <p>You can now run campaigns and track email delivery in your Brevo dashboard.</p>
            """,
            text_content="✅ Brevo Integration Test Successful! Your Smart After-Sales Campaign system is working.",
            tags=["test", "system_verification"]
        )
        
        print("📤 Sending test email...")
        
        # Send email
        api_response = api_instance.send_transac_email(test_email)
        
        print(f"✅ SUCCESS! Test email sent")
        print(f"📬 Brevo Message ID: {api_response.message_id}")
        print(f"🎯 Track this email at: https://app.brevo.com/email/transactional")
        print()
        print("📧 Check your inbox (onkar.kolekar23@vit.edu) for the test email!")
        print("If you received it, your Brevo integration is working perfectly!")
        
        return True
        
    except ApiException as e:
        print(f"❌ Brevo API Error: {e}")
        print(f"🔍 Status: {e.status}, Reason: {e.reason}")
        
        if e.status == 401:
            print("🔑 This is an authentication error. Possible causes:")
            print("   • API key is incorrect")
            print("   • IP address not whitelisted in Brevo")
            print("   • Account has restrictions")
            print(f"   • Visit: https://app.brevo.com/security/authorised_ips")
        
        return False
    except Exception as e:
        print(f"❌ General Error: {e}")
        return False

def check_brevo_account_status():
    """Check Brevo account status and settings"""
    
    print("🔍 Checking Brevo Account Status...")
    
    try:
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = settings.brevo.api_key
        
        # Try to get account info
        account_api = sib_api_v3_sdk.AccountApi(sib_api_v3_sdk.ApiClient(configuration))
        account_info = account_api.get_account()
        
        print(f"✅ Account Email: {account_info.email}")
        print(f"📊 Email Credits: {account_info.plan[0].credits}")
        print(f"🏢 Company: {account_info.company_name}")
        
        return True
        
    except ApiException as e:
        print(f"❌ Cannot access account info: {e}")
        return False
    except Exception as e:
        print(f"❌ Error checking account: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 BREVO EMAIL SERVICE TEST")
    print("=" * 60)
    print()
    
    # Test 1: Check account status
    print("TEST 1: Account Status")
    print("-" * 20)
    account_ok = check_brevo_account_status()
    print()
    
    # Test 2: Send test email
    print("TEST 2: Email Sending")
    print("-" * 20)
    email_ok = test_brevo_connection()
    print()
    
    # Summary
    print("=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    print(f"Account Status: {'✅ OK' if account_ok else '❌ FAILED'}")
    print(f"Email Sending: {'✅ OK' if email_ok else '❌ FAILED'}")
    
    if account_ok and email_ok:
        print()
        print("🎉 ALL TESTS PASSED! Your Brevo integration is working perfectly.")
        print("You can now run campaigns and emails will be delivered successfully.")
    else:
        print()
        print("⚠️  Some tests failed. Please check the errors above and:")
        print("   • Verify your Brevo API key in config/settings.py")
        print("   • Add your IP to Brevo whitelist if needed")
        print("   • Check your Brevo account status")
