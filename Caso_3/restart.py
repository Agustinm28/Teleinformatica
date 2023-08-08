import subprocess
import argparse

def delete():

    print('Deleting...')

    # Borrar MySQL
    subprocess.run(['kubectl','delete','sts','metabase-db']) # sts
    subprocess.run(['kubectl','delete','pvc','mysql-data-metabase-db-0']) # pvc
    subprocess.run(['kubectl','delete','service','mysql-service']) # service
    subprocess.run(['kubectl','delete','secret','meta-db-secrets']) # secret
    subprocess.run(['kubectl','delete','configmap','mysql-config']) # configmap

    # Borrar Metabase
    subprocess.run(['kubectl','delete','deploy','metabase']) # deployment
    subprocess.run(['kubectl','delete','service','metabase-service']) # service
    subprocess.run(['kubectl','delete','secret','metabase-secrets']) # secret
    subprocess.run(['kubectl','delete','configmap','metabase-config']) # configmap 
    subprocess.run(['kubectl','delete','ingress','metabase-ingress']) # ingress 

def start():
    print('Starting...')
    subprocess.run(['kubectl','apply','-f','.'])

def restart():
    delete()
    start()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Delete or restart Metabase and MySQL')
    parser.add_argument('-start', action='store_true', help='Start Metabase and MySQL')
    parser.add_argument('-delete', action='store_true', help='Delete Metabase and MySQL')
    parser.add_argument('-restart', action='store_true', help='Restart Metabase and MySQL')
    
    args = parser.parse_args()
    if args.restart:
        restart()
    elif args.delete:
        delete()
    elif args.start:
        start()