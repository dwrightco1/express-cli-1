import analytics
import uuid
import math
import time
import datetime

# the write_key is the Segment API authorization and identifier, without this no data submission will work. The API Key below is for Dev/Test work
analytics.write_key = 't1tdSZocQ49Tx3G66lUjJXkOXjUSYRKx'

def on_error(error, items):
    print('An error occurred:', error)

analytics.debug = True
analytics.on_error = on_error



class SegmentSession:

    def __init__(self):
        # unique for the device
        self.device_id = str(uuid.uuid3(uuid.NAMESPACE_DNS, str(uuid.getnode())))

        # unique for this session
        self.anonymousId = str(uuid.uuid1())

        # Session time is time in EPOC that must be passed to Segment in each track event to ensure that a single session is maintained. The client side CLI should generate this and submit the string with each API submission
        self.session_time = str(math.floor(time.time()))



    def send_track(self, wizard_step, wizard_state, wizard_progress, wizard_name, user_id=None):

        track_dict = {
            'anonymousId': self.anonymousId,
            'wizard_step': wizard_step,
            'wizard_state': wizard_state,
            'wizard_progress': wizard_progress,
            'wizard_name': wizard_name,
            'device_id': self.device_id,
            'deployment_type': 'BareOS'
        }
        if user_id:
            track_dict['user_id'] = user_id

        analytics.track(self.anonymousId, wizard_name, track_dict,
            anonymous_id=self.anonymousId,
            # The 'integrations array begin passed below is how the 'session' identifier is passed into Amplitude
            integrations={
                'Amplitude': {
                    'session_id': self.session_time
                }
            }
        )

    def send_identify(self):
        analytics.identify('', {
            'anonymousId': self.anonymousId,
            'device_id': self.device_id,
            'bare_os_deployment': 'Activated',
            'bare_os_deployment_state': 'Initialized',
            # all DATE and TIME submissions need to be in ISO 8601 format
            'createdAt': datetime.datetime.now().isoformat(),
            },
           anonymous_id=self.anonymousId,
        )