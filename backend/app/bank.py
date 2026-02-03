from __future__ import annotations

QUESTION_BANK = [
  # --- Core baseline (ALL) ---
  {"id":"CORE_A1","persona":"ALL","domain":"A","type":"OPEN",
   "prompt":"In your own words, what is the difference between traditional AI and generative AI?"},
  {"id":"CORE_B1","persona":"ALL","domain":"B","type":"OPEN",
   "prompt":"Give one good use case for generative AI in your work, and one use case where it would be risky or low value."},
  {"id":"CORE_C1","persona":"ALL","domain":"C","type":"OPEN",
   "prompt":"What kinds of information should never be pasted into an AI tool unless explicitly approved and protected?"},
  {"id":"CORE_D1","persona":"ALL","domain":"D","type":"OPEN",
   "prompt":"If an AI output appears biased or unfair, what would you do before using it?"},
  {"id":"CORE_E1","persona":"ALL","domain":"E","type":"OPEN",
   "prompt":"What elements make a prompt effective (context, constraints, format, examples, etc.)?"},
  {"id":"CORE_F1","persona":"ALL","domain":"F","type":"OPEN",
   "prompt":"How do you validate an AI-generated answer before acting on it?"},
  {"id":"CORE_G1","persona":"ALL","domain":"G","type":"OPEN",
   "prompt":"Who should be accountable for approving AI use cases (business, IT, security, leadership)? Why?"},
  {"id":"CORE_F2","persona":"ALL","domain":"F","type":"MCQ",
   "prompt":"The AI gives a confident answer with no sources. What’s your next step?",
   "options":[
      "Use it as-is if it sounds right",
      "Ask the AI for sources/assumptions and verify with trusted references",
      "Ignore it entirely; AI is never useful",
      "Forward it to someone else without checking"
   ]},

  # --- Executive ---
  {"id":"EXEC_B2","persona":"EXECUTIVE","domain":"B","type":"OPEN",
   "prompt":"How would you prioritize which AI initiatives to fund first (mission impact, readiness, risk, speed, cost)?"},
  {"id":"EXEC_C2","persona":"EXECUTIVE","domain":"C","type":"OPEN",
   "prompt":"What AI-related risk would you not accept even if the business case is strong?"},
  {"id":"EXEC_G2","persona":"EXECUTIVE","domain":"G","type":"OPEN",
   "prompt":"What does 'human-in-the-loop' mean for high-impact decisions in your organization?"},
  {"id":"EXEC_F2","persona":"EXECUTIVE","domain":"F","type":"OPEN",
   "prompt":"What metrics would convince you an AI pilot is ready to scale?"},
  {"id":"EXEC_D2","persona":"EXECUTIVE","domain":"D","type":"OPEN",
   "prompt":"If AI contributes to a harmful decision, how do you think about accountability and oversight?"},

  # --- PM ---
  {"id":"PM_G2","persona":"PM","domain":"G","type":"OPEN",
   "prompt":"How would you write acceptance criteria for an AI assistant (quality, safety, latency, auditability)?"},
  {"id":"PM_C2","persona":"PM","domain":"C","type":"OPEN",
   "prompt":"How would you ensure the AI solution only uses approved data and respects access controls?"},
  {"id":"PM_F2","persona":"PM","domain":"F","type":"OPEN",
   "prompt":"How would you test an AI feature differently than deterministic software?"},
  {"id":"PM_D2","persona":"PM","domain":"D","type":"OPEN",
   "prompt":"If the AI produces a harmful output in production, what is your incident response and rollback plan?"},
  {"id":"PM_B2","persona":"PM","domain":"B","type":"OPEN",
   "prompt":"What change management and adoption risks do you expect, and how would you address them?"},

  # --- Business user ---
  {"id":"BUS_B2","persona":"BUSINESS_USER","domain":"B","type":"OPEN",
   "prompt":"Describe a repeatable task you do. Where could AI help (drafting, summarizing, analysis, generating options)?"},
  {"id":"BUS_E2","persona":"BUSINESS_USER","domain":"E","type":"OPEN",
   "prompt":"Write a prompt to summarize a long report into: decisions, risks, and actions, in bullet points."},
  {"id":"BUS_F2","persona":"BUSINESS_USER","domain":"F","type":"OPEN",
   "prompt":"How do you detect when the AI is hallucinating or making unsupported claims?"},
  {"id":"BUS_D2","persona":"BUSINESS_USER","domain":"D","type":"OPEN",
   "prompt":"If AI suggests a hiring shortlist or evaluation, what checks would you apply before using it?"},
  {"id":"BUS_C2","persona":"BUSINESS_USER","domain":"C","type":"OPEN",
   "prompt":"What would you do if someone asks you to paste sensitive content into an AI tool to save time?"},

  # --- End user ---
  {"id":"END_A2","persona":"END_USER","domain":"A","type":"OPEN",
   "prompt":"What tasks would you feel comfortable using AI for today?"},
  {"id":"END_F2","persona":"END_USER","domain":"F","type":"OPEN",
   "prompt":"When would you not trust an AI answer? Give an example."},
  {"id":"END_C2","persona":"END_USER","domain":"C","type":"OPEN",
   "prompt":"Name two things you should avoid sharing with an AI assistant."},
  {"id":"END_E2","persona":"END_USER","domain":"E","type":"OPEN",
   "prompt":"You need an email draft requesting info from another department. What would you tell the AI so it uses the right tone and details?"},
  {"id":"END_G2","persona":"END_USER","domain":"G","type":"OPEN",
   "prompt":"If AI gives you a policy interpretation, what should you do next before acting on it?"},

  # --- IT Engineer ---
  {"id":"ITENG_C2","persona":"IT_ENGINEER","domain":"C","type":"OPEN",
   "prompt":"What technical controls would you implement to prevent sensitive data leakage when integrating AI tools?"},
  {"id":"ITENG_F2","persona":"IT_ENGINEER","domain":"F","type":"OPEN",
   "prompt":"How would you validate AI outputs in a production workflow to reduce hallucinations and errors?"},
  {"id":"ITENG_E2","persona":"IT_ENGINEER","domain":"E","type":"OPEN",
   "prompt":"Describe how you would structure prompts or system instructions to enforce safe behavior in an AI assistant."},
  {"id":"ITENG_D2","persona":"IT_ENGINEER","domain":"D","type":"OPEN",
   "prompt":"What monitoring and logging would you set up to detect harmful or non‑compliant AI outputs?"},
  {"id":"ITENG_G2","persona":"IT_ENGINEER","domain":"G","type":"OPEN",
   "prompt":"Who should sign off on deploying an AI feature, and what evidence should be required?"},

  # --- IT Architect ---
  {"id":"ITARCH_B2","persona":"IT_ARCHITECT","domain":"B","type":"OPEN",
   "prompt":"How would you evaluate which AI use cases belong in the enterprise architecture roadmap?"},
  {"id":"ITARCH_C2","persona":"IT_ARCHITECT","domain":"C","type":"OPEN",
   "prompt":"How would you design data boundaries and access controls for AI systems across multiple domains?"},
  {"id":"ITARCH_F2","persona":"IT_ARCHITECT","domain":"F","type":"OPEN",
   "prompt":"What quality and validation gates would you require before scaling an AI system?"},
  {"id":"ITARCH_D2","persona":"IT_ARCHITECT","domain":"D","type":"OPEN",
   "prompt":"How would you ensure responsible AI principles are embedded in system architecture and delivery?"},
  {"id":"ITARCH_G2","persona":"IT_ARCHITECT","domain":"G","type":"OPEN",
   "prompt":"What governance model would you propose for AI systems operating across business units?"},

  # --- Scenarios (ALL) ---
  {"id":"SCN_C1","persona":"ALL","domain":"C","type":"OPEN",
   "prompt":"Scenario: You have a document with internal details and want AI to summarize it. What do you do to stay safe and compliant?"},
  {"id":"SCN_F1","persona":"ALL","domain":"F","type":"OPEN",
   "prompt":"Scenario: AI generates a confident procurement recommendation with no sources and you’re under deadline. What steps do you take?"},
]
