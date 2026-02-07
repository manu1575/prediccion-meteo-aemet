import smtplib
from email.message import EmailMessage
import os

def enviar_email(pdf_path):
    msg = EmailMessage()
    msg["Subject"] = "Predicción meteorológica semanal"
    msg["From"] = os.environ["SMTP_USER"]
    msg["To"] = os.environ["EMAIL_RECEIVER"]
    msg.set_content("Adjunto informe meteorológico semanal.")

    with open(pdf_path, "rb") as f:
        msg.add_attachment(
            f.read(),
            maintype="application",
            subtype="pdf",
            filename=os.path.basename(pdf_path)
        )

    with smtplib.SMTP_SSL(os.environ["SMTP_SERVER"], int(os.environ["SMTP_PORT"])) as s:
        s.login(os.environ["SMTP_USER"], os.environ["SMTP_PASSWORD"])
        s.send_message(msg)

if __name__ == "__main__":
    pdf = max(
        [f"outputs/{f}" for f in os.listdir("outputs") if f.endswith(".pdf")],
        key=os.path.getctime
    )
    enviar_email(pdf)
