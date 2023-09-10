import base64
import json
import googleapiclient.discovery

def disable_serviceAccount(event, context):
    """Disables the service account that created bulk VMs
    """
    pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    msg_json = json.loads(pubsub_message)
    proto_payload = msg_json['protoPayload']
    resource_name = proto_payload['resourceName']
    name_tokens = resource_name.split('/')
    email = proto_payload['authenticationInfo']['principalEmail']
    subject = proto_payload['authenticationInfo']['principalSubject']
    subject_items = subject.split(':')
    project = name_tokens[1]
    # fetch the proper email id and verify if its user/service account.
    if subject_items[0] == 'user':
      print('It is a User:%s triggered bulkInser Method -- can not disable users' % (email))
    else:
      # IAM API
      keyId = proto_payload['authenticationInfo']['serviceAccountKeyName']
      keyId_items = keyId.rsplit("/",1)
      service = googleapiclient.discovery.build('iam', 'v1', cache_discovery=False)
      service.projects().serviceAccounts().disable(name='projects/%s/serviceAccounts/%s' % (project, email)).execute()
      service.projects().serviceAccounts().keys().delete(name='projects/%s/serviceAccounts/%s/keys/%s' % (project, email, keyId_items[1])).execute()
      print("Disabled %s service account & Deleted its Key as well" % email)