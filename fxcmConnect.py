import fxcmpy
import yaml

def connection():
    with open('config.yaml') as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
        token = data.get("token")
        print(token)
    #connect to broker
    con = fxcmpy.fxcmpy(access_token=token, log_file='log.txt', server='demo')

    return con