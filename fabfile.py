from fabric.api import get, env, cd, run, local

env.hosts = ['txl11@dougal.union.ic.ac.uk:10022']

def pull_mongo():
    with cd('/home/sysadmin/mongo_backups'):
        local('rm -rf dump')
        run('mongodump -h localhost -d mums_and_dads --authenticationDatabase=admin -u root -p ')
        get('dump', '.')
        run('rm -rf dump')
        local('mongorestore -h localhost --db madass --drop ./dump/mums_and_dads')