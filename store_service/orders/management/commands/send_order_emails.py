from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.db import transaction
from django.utils import timezone
from orders.models import EmailJob,DownloadGrant
from orders.fulfillment import grant,digest
from datetime import timedelta
from orders.copy import COPY
class Command(BaseCommand):
 help='Send queued transactional messages only; run from a private scheduled worker.'
 def handle(self,*args,**options):
  count=0
  # Per-job lock serializes cooperating workers. SMTP cannot guarantee exactly-once delivery after a crash.
  for pk in EmailJob.objects.filter(sent_at__isnull=True,attempts__lt=8).values_list('pk',flat=True)[:100]:
   with transaction.atomic():
    job=EmailJob.objects.select_for_update().select_related('order').get(pk=pk)
    if job.sent_at or job.order.status!='paid':continue
    token=job.link.split('/download/')[-1].split('/')[0]
    if not DownloadGrant.objects.filter(order=job.order,token_hash=digest(token),revoked=False,expires_at__gt=timezone.now()+timedelta(minutes=5)).exists():
     job.link=grant(job.order,job.kind);job.save(update_fields=['link'])
    job.attempts+=1;job.save(update_fields=['attempts']);c=COPY[job.order.language]
    body=c['emailBody']+'\n\n'+job.link+'\n\n'+c['emailEdition']+' '+job.order.language.upper()+'\n'+c['immediate']+'\n\nOrder: '+str(job.order_id)+'\nEUR 2.99\nali@alialkhuzaee.com'
    try:send_mail(c['emailSubject'],body,None,[job.order.email],fail_silently=False)
    except Exception:continue
    job.sent_at=timezone.now();job.save(update_fields=['sent_at']);count+=1
  self.stdout.write(f'Sent {count} transactional email(s).')
