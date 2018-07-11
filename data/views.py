import base64
import boto3
import csv
import requests
import tempfile

from flask import Blueprint, current_app

data_bp = Blueprint('data', __name__)
s3 = boto3.client('s3')


class ZendeskConnector(object):

    def __init__(self):
        self.headers = self._get_headers()
        self.metrics_url = self._get_metrics_url()
        self.rows = []
        self.organizations = {}
        self.users = {}
        self.csv_fields = [
            u'date_created',
            u'ticket_id',
            u'assignee_name',
            u'ticket_subject',
            u'organization',
            u'type',
            u'trello_card',
            u'reason_code',
            u'product_area'
        ]

    def _get_headers(self):
        return {
            u'Authorization': u'Basic {}'.format(
                base64.b64encode(current_app.config['ZENDESK_TOKEN']))
        }

    def _get_metrics_url(self):
        return u'{}/api/v2/views/{}/execute.json' \
              .format(current_app.config['ZENDESK_URL'],
                      current_app.config['ZENDESK_VIEW'])

    def _get_request(self, url):
        r = requests.get(url, headers=self.headers)
        return r.json()

    def _update_metrics_data(self, response):
        self.rows.extend(response[u'rows'])
        self.organizations.update(
            {org[u'id']: org[u'name'] for org in response[u'organizations']})
        self.users.update(
            {user[u'id']: user[u'name'] for user in response[u'users']})

    def _create_data_table(self):
        data_table = []
        for row in self.rows:
            data_table.append([
                row[u'created'].split("T")[0],  # date created

                row[u'ticket'][u'id'],  # ticket id

                self.users[row[u'assignee_id']],  # assignee name

                row[u'ticket'][u'subject'],  # ticket subject

                self.organizations[row[u'organization_id']]\
                if row[u'organization_id'] else "",  # organization

                row[u'custom_fields'][0][u'name']\
                if row[u'custom_fields'][0] else "",  # type

                row[u'custom_fields'][1][u'name']\
                if row[u'custom_fields'][1] else "",  # trello card

                row[u'custom_fields'][2][u'value']\
                if row[u'custom_fields'][2] else "",  # reason code

                row[u'custom_fields'][3][u'name']\
                if row[u'custom_fields'][3] else "",  # product area
            ])
        return data_table

    def _write_to_s3(self, data_table):
        with tempfile.NamedTemporaryFile() as tmp_csv:
            writer = csv.writer(tmp_csv, delimiter=',')
            writer.writerow(self.csv_fields)
            writer.writerows(data_table)
            tmp_csv.seek(0)
            s3.upload_fileobj(tmp_csv,
                              current_app.config['S3_BUCKET_NAME'],
                              'zendesk-data.csv')

    def get_and_store_metrics_in_s3(self):
        response = self._get_request(self.metrics_url)
        self._update_metrics_data(response)
        while response[u'next_page']:
            response = self._get_request(response[u'next_page'])
            self._update_metrics_data(response)
        data_table = self._create_data_table()
        self._write_to_s3(data_table)


@data_bp.route('/get_data')
def get_data():
    zendesk = ZendeskConnector()
    zendesk.get_and_store_metrics_in_s3()
    return 'OK'
