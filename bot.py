from telegram import Update, Poll
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import re

# मजबूत MCQ पहचानने वाला फंक्शन
def extract_mcqs(text):
    mcq_blocks = re.split(r'\n{2,}|\n(?=प्रश्न\s?\d+[:\-])', text.strip())
    mcqs = []

    for block in mcq_blocks:
        block = block.strip()

        # प्रश्न
        question_match = re.search(r'^(.*?)(?=\n\s*[a-dA-D1-4][\)\.] ?)', block, re.DOTALL)
        raw_question = question_match.group(1).strip() if question_match else None
        if raw_question:
            question = re.sub(r'^\s*(प्रश्न|ques|question|q)?\.?\s*[\d०-९]+[\:\)\.\-–—]?\s*', '', raw_question, flags=re.IGNORECASE).strip()
        else:
            question = None

        # विकल्प
        options = re.findall(r'^[ \t]*[a-dA-D1-4][\)\.] ?(.*)', block, re.MULTILINE)

        # उत्तर
        answer_match = re.search(r'उत्तर[:\-]?\s*([a-dA-D1-4])', block, re.IGNORECASE)
        correct_index = None
        correct_text = ""
        if answer_match:
            ans = answer_match.group(1).lower()
            if ans in 'abcd':
                correct_index = 'abcd'.index(ans)
                correct_text = options[correct_index] if correct_index < len(options) else ""
            elif ans in '1234':
                correct_index = int(ans) - 1
                correct_text = options[correct_index] if correct_index < len(options) else ""

        # व्याख्या
        explanation_match = re.search(r'व्याख्या[:\-]?(.*)', block, re.DOTALL | re.IGNORECASE)
        explanation = explanation_match.group(1).strip() if explanation_match else ""

        full_explanation = ""
        if correct_text:
            full_explanation += f"उत्तर: {correct_text.strip()}"
        if explanation:
            full_explanation += f"\n\n{explanation.strip()}"

        if question and options:
            mcqs.append((question, options, correct_index, full_explanation))

    return mcqs

# Telegram handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    mcqs = extract_mcqs(text)

    if not mcqs:
        await update.message.reply_text("कोई वैध MCQ नहीं मिला। कृपया सही प्रारूप में भेजें।")
        return

    for i, (question, options, correct_index, explanation) in enumerate(mcqs):
        await context.bot.send_poll(
            chat_id=update.effective_chat.id,
            question=question,
            options=options,
            type=Poll.QUIZ,
            correct_option_id=correct_index if correct_index is not None else 0,
            explanation=explanation if explanation else None
        )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("MCQs भेजें — मैं उन्हें साफ करके Poll में बदल दूँगा, उत्तर व व्याख्या सहित।")

def main():
    app = ApplicationBuilder().token("YOUR_BOT_TOKEN_HERE").build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("बोट चालू है...")
    app.run_polling()

if __name__ == "__main__":
    main()