# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Notification'
        db.create_table('mailru_money_notification', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=15)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=15)),
            ('item_number', self.gf('django.db.models.fields.CharField')(max_length=30, db_index=True)),
            ('issuer_id', self.gf('django.db.models.fields.CharField')(max_length=30, db_index=True)),
            ('serial', self.gf('django.db.models.fields.CharField')(max_length=15)),
            ('auth_method', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('mailru_money', ['Notification'])

    def backwards(self, orm):
        # Deleting model 'Notification'
        db.delete_table('mailru_money_notification')

    models = {
        'mailru_money.notification': {
            'Meta': {'object_name': 'Notification'},
            'auth_method': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'issuer_id': ('django.db.models.fields.CharField', [], {'max_length': '30', 'db_index': 'True'}),
            'item_number': ('django.db.models.fields.CharField', [], {'max_length': '30', 'db_index': 'True'}),
            'serial': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '15'})
        }
    }

    complete_apps = ['mailru_money']