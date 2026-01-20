import aiosmtplib
from email.mime.text import  MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List
import os
from app.core.logger import logger

class EmailService:
    # send emails using Gmail smtp
    
    def __init__(self):
        self.smtp_host=os.getenv("SMTP_HOST","smtp.gmail.com")
        self.smtp_port=int(os.getenv("SMTP_PORT",587))
        self.smtp_user=os.getenv("SMTP_USER")
        self.smtp_password=os.getenv("SMTP_PASSWORD")
        self.from_email=os.getenv("SMTP_FROM_EMAIL")
        self.from_name=os.getenv("SMTP_FROM_NAME","Facematch")
        
        
    async def send_email(
        self,
        to_emails:List[str],
        subject:str,
        body:str,
        is_html:bool=False
    ):
        # Validate SMTP configuration
        if not self.smtp_user or not self.smtp_password or not self.from_email:
            logger.warning("Email service not configured. Skipping email send.")
            return False
            
        try:
            #ceating e-mail message
            message=MIMEMultipart("alternative")
            message["From"]=f"{self.from_name} <{self.from_email}>"
            message["To"]=", ".join(to_emails)
            message["Subject"]=subject
            #Adding body
            
            if is_html:
                message.attach(MIMEText(body,'html'))
            else:
                message.attach(MIMEText(body,'plain'))
                
            #connecting to gmal
            logger.info(f"Connecting to {self.smtp_host}:{self.smtp_port}")
            
            async with aiosmtplib.SMTP(
                hostname=self.smtp_host,
                port=self.smtp_port,
                start_tls=True
            ) as smtp:
                await smtp.login(self.smtp_user,self.smtp_password)
                logger.info(f"Logging in smtp server")
                await smtp.send_message(message)
                logger.info("Email sent successfully")
            
            return True
        except Exception as e:
            logger.error(f"Failed to send email: {e}", exc_info=True)
            return False
        
    async def send_attendance_marked_email(
        self,
        employee_name:str,
        employee_email:str,
        time_in:str,
        date:str
    ):
        """Send confirmation when attendance is marked"""
        subject = "Attendance marked successfully"
        
        body = f"""
Hello {employee_name},

Your attendance has been marked successfully! 

Details:
- Date: {date}
- Time: {time_in}
- Status: Present

Thank you for being on time!

Best regards,
FaceMatch Attendance System
        """.strip()
        
        return await self.send_email(
            to_emails=[employee_email],
            subject=subject,
            body=body
        )
    
    async def send_attendance_notification_to_admin(
        self,
        employee_name:str,
        employee_id:str,
        time_in:str,
        date:str
    ):
        """Notify admin when someone marks attendance"""
        admin_email = os.getenv("ADMIN_EMAIL")
        if not admin_email:
            logger.warning("ADMIN_EMAIL not configured")
            return False
        
        subject = f"📊 Attendance: {employee_name}"
        
        body = f"""
New attendance recorded:

Employee: {employee_name} (ID: {employee_id})
Date: {date}
Time: {time_in}
Status: Present

---
FaceMatch System
        """.strip()
        
        return await self.send_email(
            to_emails=[admin_email],
            subject=subject,
            body=body
        )
                
#ccreating instance
email_service=EmailService()