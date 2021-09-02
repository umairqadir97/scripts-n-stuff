# Move objects to correct bucket prefix

import sys
sys.path.append('../custom_modules/aws_modules')
import general_modules as mod

MFA_Profile = 'unit21-prod-mfa'
AWS_Region = 'us-west-2'

ses = mod.set_session(MFA_Profile, AWS_Region)


