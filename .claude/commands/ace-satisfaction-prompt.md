# ACE Satisfaction Feedback Prompt

You just completed a work session with the user.

Your goal is to collect structured user satisfaction feedback to improve future performance through the ACE (Agentic Context Engineering) framework.

## Session Summary

$SESSION_SUMMARY

## Satisfaction Check

On a scale of 1-5, how satisfied are you with this work session?

**Rating Scale:**
- 1️⃣ **Very dissatisfied** - Major issues, nothing worked, complete failure
- 2️⃣ **Dissatisfied** - Some issues, not what I expected, needs significant improvement
- 3️⃣ **Neutral** - It's okay, room for improvement, met minimum expectations
- 4️⃣ **Satisfied** - Good work, met expectations, would use again
- 5️⃣ **Very satisfied** - Excellent work, exceeded expectations, highly effective

---

**Please provide your rating (1-5)**: [Awaiting user input]

**What worked well** (optional): [What did you find helpful or effective?]

**What could be improved** (optional): [What would make future sessions better?]

---

## Instructions for Capturing Feedback

After the user responds, structure the feedback as follows:

```json
{
  "score": <1-5>,
  "positive_feedback": "<what worked well>",
  "improvement_areas": "<what could be improved>",
  "timestamp": "<current ISO timestamp>"
}
```

This feedback will be:
1. Attached to the execution trace (Generator)
2. Analyzed to identify patterns (Reflector)
3. Used to weight insights in playbook (Curator)

**Key Principles:**
- High satisfaction (4-5) → Actions taken are success patterns
- Low satisfaction (1-2) → Actions taken are failure modes
- Specific feedback → Better insights and improvements

Thank you for helping the ACE framework learn and improve!
