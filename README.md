# Hisaab AI Assistant

Youtube video demo: https://youtu.be/Oi4nUFsumOU

NOTE: Curennt application is ALREADY hosted and running. If you want to test out Hisaab for yourself simply go to this number: 03008224731 (+92 3008224731) and message "Salam" or "Hello" to get started

NOTE: Below setup guide shares how to run the project locally, for production you need to host the hisaab database and agent memory database online, as well as the entire webhook server

#### **What is this Project?**
Pakistan has 3-4 million small retail shops. Most shopkeepers track sales and credit (udhar) in physical notebooks which is messy, prone to errors, and impossible to search. 42% of adults can't read well, making written record-keeping even harder.

The core problem: shopkeepers forget who owes what, lose money from unpaid credit, can't generate reports for taxes, and have no systematic way to follow up on payments. Credit recovery rates are terrible because there's no organized system.

I'm building Hisaab, a WhatsApp voice bot where shopkeepers can simply send voice notes about their transactions in Urdu: "Ali korangi wala ne 500 rupay kay unday liye udhar" and the system automatically maintains clean digital records, tracks customer balances, sends payment reminders, and generates daily/monthly reports

The system understands natural Urdu speech, making bookkeeping accessible for low-literacy users. WhatsApp means zero app downloads, they already use it daily.

With this shopkeepers could ask the AI Agent stuff like:
 - "Rizwan ne 500 rupay ke biscuits liye udhar" → System records transaction
- "Ali ka kitna udhar hai?" → Instant balance check
- "Hassan bhai ne 1000 diye" → Payment recorded, balance updated
Analytical queries:
 - "Kon kon log hai jinho nein ab tak koi udhar ki repayment nahi ki?"
 - "Kin logon nay sab se ziada udhaar liya wa hai"
 - "Ali ki poori udhaar aur payment history dikhao"


This is just the beginning, we plan to add tracking for supplier payments, daily transaction etc... digitalizing the whole Pakistani small retail shops market.

Fintech Vision:

Beyond record-keeping, Hisaab aims to help formalize Pakistan’s informal economy.

It can integrate with bank payments and mobile wallets like Easypaisa or JazzCash, allowing customers to repay credit digitally. This creates a verifiable financial trail, helping shopkeepers qualify for microfinance loans and enabling AI-based credit scoring, directly supporting the hackathon’s Fintech goals.

Additionally, Hisaab’s structured transaction data can align with FBR reporting, allowing small shopkeepers to generate automated income summaries and contribute to Pakistan’s documented economy. 

This helps the government track small business activity, expand tax documentation, and encourage financial transparency.

In the long run, Hisaab can evolve into a national-scale AI-driven microfinance and compliance platform, turning informal retailers into financially visible, creditworthy businesses. With its voice-first design and WhatsApp integration, Hisaab makes digital finance inclusive, practical, and truly “Made for Pakistan.”

**Key Features:**
- 🎤 **Voice-First Interface** - Send voice messages in Urdu, get voice responses
- 📊 **Smart Credit Tracking** - Automatically calculates balances and transaction history  
- 🔍 **Intelligent Name Matching** - Handles customer nicknames and variations
- 💾 **Persistent Memory** - Remembers all transactions and customer details
- 📱 **WhatsApp Integration** - Works directly through WhatsApp Business API
- 🗣️ **Natural Urdu Responses** - Responds in proper Urdu script, not Roman Urdu


#### **How it works?**

This project is composed of 4 core modules:

1. **WhatsApp Integration** - Handles incoming voice/text messages and sends responses
2. **Voice Processing** - Transcribes voice messages and generates voice responses  
3. **AI Agent** - LangGraph-powered agent that processes requests and manages database
4. **Database Management** - SQLite-based credit tracking with persistent memory

#### **Project Flow**

1. **WhatsApp Webhook**  
    A WhatsApp message (text or voice) is received via webhook, triggering the agent workflow.

2. **Voice Processing**  
    - **Incoming**: Voice messages are transcribed using OpenAI Whisper
    - **Outgoing**: Text responses are converted to voice using UpliftAI TTS

3. **AI Agent Processing**  
    The LangGraph agent processes the user request:
    - **Authentication**: Verifies shopkeeper registration
    - **Smart Name Matching**: Handles customer name variations and nicknames
    - **Database Operations**: Records transactions, updates balances, retrieves history
    - **Proactive Responses**: Provides additional helpful information

4. **Response Delivery**  
    The agent sends both text and voice responses back through WhatsApp.

###### **Technical Breakdown**

- **LangGraph** – Agent framework for building conversational AI workflows with persistent memory
- **UpliftAI** – Text-to-speech service for generating natural Urdu voice responses
- **OpenAI Whisper** – Speech-to-text for transcribing Urdu voice messages
- **FastAPI** – Lightweight web server handling WhatsApp webhooks
- **SQLite** – Local database for credit tracking with persistent agent memory
- **WhatsApp Business API** – Official WhatsApp integration for messaging

**Why this stack?**
- Voice-first design matches Pakistani business communication patterns
- Local database ensures data privacy and offline functionality
- LangGraph provides robust conversation memory and tool integration
- Minimal external dependencies reduce costs and complexity

---

## **How to setup and run locally:**

Prerequisites:
You should be familiar with WhatsApp Business API, LangGraph, FastAPI, and general development tools like git, Python, etc.

#### **1. Project Setup**

**1.1. Clone the Repository**

First, clone the project repository to your local machine:

```bash
git clone https://github.com/Muzamil-Ahmed/Hisaab-public
cd hisaab-public
```

**1.2. Install Dependencies**

Install all required Python packages using `pip`:

```bash
pip install -r requirements.txt
```

**1.3. Configure Environment Variables**

Create a `.env` file in the root directory of your project (same level as `requirements.txt`):

```env
# WhatsApp Business API Configuration
WEBHOOK_VERIFY_TOKEN=your_webhook_verify_token
WHATSAPP_ACCESS_TOKEN=your_whatsapp_access_token
PHONE_NUMBER_ID=your_phone_number_id

# AI Services
OPENAI_API_KEY=your_openai_api_key
UPLIFT_API_KEY=your_uplift_api_key

# Optional: LangSmith for tracing and debugging
LANGSMITH_API_KEY=your_langsmith_api_key
LANGSMITH_TRACING=true
```

---
#### **2. WhatsApp Business API Setup:**

**2.1. Create WhatsApp Business Account**

1. Go to [Meta for Developers](https://developers.facebook.com/) and create a developer account
2. Create a new app and add WhatsApp Business API product
3. Set up a WhatsApp Business Account (you can use a test number initially)

**2.2. Configure Webhook**

1. In your WhatsApp Business API settings, go to **Configuration**
2. Set the **Webhook URL** to your ngrok URL (we'll set this up later): `https://your-ngrok-url.ngrok.io/webhook`
3. Set the **Verify Token** to match your `WEBHOOK_VERIFY_TOKEN` in `.env`
4. Subscribe to `messages` events

**2.3. Get Required Credentials**

From your WhatsApp Business API dashboard,  and put it in env (you may need to update Access token from time to time):
- **Access Token** → `WHATSAPP_ACCESS_TOKEN`
- **Phone Number ID** → `PHONE_NUMBER_ID`
- **Webhook Verify Token** → `WEBHOOK_VERIFY_TOKEN`

---
#### **3. UpliftAI Setup**

**3.1. Create UpliftAI Account**

1. Go to [UpliftAI](https://upliftai.org/) and sign up for an account
2. Navigate to API Keys section and generate a new API key
3. Copy the API key and update `UPLIFT_API_KEY` in your `.env` file

**3.2. Voice Configuration**

The project uses a pre-configured voice ID (`v_8eelc901`) from Uplift AI, you can alter it for differnt voice styles. You can:
- Test different voice IDs from UpliftAI's voice library
- Modify the voice ID in `app/voice.py` if needed
- Adjust output format if required (currently set to `MP3_22050_128`)

---
#### **4. Database Setup**

**4.1. Initialize Database**

Run the database setup script to create tables and add sample data:

```bash
python app/local_database/setup.py
```

This will:
- Create SQLite database with required tables
- Add sample shopkeeper and customer data
- Generate realistic transaction history for testing

**4.2. Database Schema**

The database includes three main tables:
- `shopkeepers` - Store information for each shopkeeper
- `customers` - Customer details and balance tracking
- `credit_transactions` - Detailed transaction history

---
#### **5. OpenAI Setup**

**5.1. Get OpenAI API Key**

1. Go to [OpenAI Platform](https://platform.openai.com/) and create an account
2. Navigate to API Keys section and create a new secret key
3. Copy the API key and update `OPENAI_API_KEY` in your `.env` file

**5.2. Model Configuration**

The project uses:
- `gpt-4o` for the main LangGraph agent
- `gpt-4o-mini-transcribe` for voice transcription

You can modify these in `app/agent/graph.py` and `app/voice.py` respectively.

---
#### **6. Run the Application**

**6.1. Start FastAPI Server**

In your terminal, start the FastAPI application:

```bash
uvicorn app.main:app --reload --port 8000
```

Your webhook is now running locally at `http://localhost:8000`

**6.2. Setup ngrok for Public Access**

Since WhatsApp needs to send webhooks to your local machine, use `ngrok` to create a public URL:

1. Download and install [ngrok](https://ngrok.com/)
2. Open a new terminal window
3. Start ngrok to expose your FastAPI server:

```bash
ngrok http 8000
```

4. Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`)
5. Update your WhatsApp webhook URL to: `https://abc123.ngrok.io/webhook` (found in configuration under "Callback URL")

**6.3. Update ngrok URL in Code**

In `app/main.py`, update the ngrok URL under handle message:
(This endpoint add proper MP3 mime type before sending audio to whatsapp)
```python
"https://your-actual-ngrok-url.ngrok-free.app"  # Replace with your actual ngrok URL
```

---
#### **7. Testing the Application**

**7.1. Test Webhook Verification**

After inputting the webhook on whatsapp along with the access token, if webhook is working properly, whatsapp should show no error after clicking "Verify and save" (Webhook successfully verified)

**7.2. Send Test Messages**

1. Send a WhatsApp message to your business number
2. Try both text and voice messages
3. Test common commands:
   - "سلام" (greeting)
   - "علی کا کتنا ادھار ہے" (check balance)
   - "فاطمہ نے پانچ سو روپے دیے" (record payment)

**7.3. Run Tests**

You can also execute the test suite to verify everything is working:

```bash
pytest tests/
```

---
#### **8. (Optional) Deploying the Application**

**8.1. Docker Deployment**

The project includes a Dockerfile for containerized deployment. Simply use the Dockerfile which is already in the project and build and deploy a Docker image to any cloud platform, I personally used used Google Cloud Run but you may choose any.


**8.2. Cloud Deployment**

Deploy to any cloud platform that supports Python applications:
- **Google Cloud Run** (recommended for serverless)
- **AWS Elastic Beanstalk**
- **Heroku**
- **DigitalOcean App Platform**

**8.3. Production Considerations**

(You are required to host the database properly on PostrgresSQL, MySQL or any other type of your choice and connect the application with it)

For production deployment:
- Use a production-grade database (PostgreSQL, MySQL)
- Set up proper logging and monitoring
- Implement rate limiting
- Set up backup strategies

---

## **Usage Examples**

### **New User Onboarding**
```
User: "السلام علیکم"
Hisaab: "السلام علیکم! میں ہسّاب ہوں۔ میں آپ کے دکان کے ادھار کے ریکارڈ رکھتی ہوں..."
```

### **Recording Credit**
```
User: "علی نے پانچ سو کے انڈے لیے ادھار"
Hisaab: "ٹھیک ہے، میں نے علی کا پانچ سو روپے ادھار لکھ دیا۔ اب ان کا کل 1500 روپے ادھار ہے۔"
```

### **Checking Balance**
```
User: "علی کا کتنا ادھار ہے"
Hisaab: "علی کا ابھی 1500 روپے بنتے ہیں"
```

### **Recording Payment**
```
User: "فاطمہ نے ہزار روپے دیے"
Hisaab: "بہت اچھا، فاطمہ کی ایک ہزار روپے ادائیگی لکھ دی۔ اب ان کا 500 روپے بنتے ہیں۔"
```

---

## **Project Structure**

```
hisaab-ai-assistant/
├── app/
│   ├── agent/
│   │   ├── graph.py          # LangGraph agent definition
│   │   ├── state.py          # Agent state schema
│   │   ├── tools.py          # Database tools
│   │   └── prompt.py         # System prompts
│   ├── local_database/
│   │   ├── setup.py          # Database initialization
│   │   ├── hisaab.db         # SQLite database (create by running setup.py)
│   │   └── agent_memory.db  # Agent memory storage (automatically created at runtime if doesnt exist)
│   ├── main.py               # FastAPI application
│   ├── whatsapp.py           # WhatsApp API utilities
│   └── voice.py              # Voice processing utilities
├── tests/
│   └── test_whatsapp.py      # Test suite
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

**Built with ❤️ for Pakistani shopkeepers**
#UraanAITechathon #UraanAI
