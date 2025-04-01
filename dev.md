```
cd aca-py
source .venv_von_network/bin/activate
cd von-network
./manage start 193.138.1.21 WEB_SERVER_HOST_PORT=80 "LEDGER_INSTANCE_NAME=My Ledger" --logs
```

```
cd aca-py
source .venv_tails-server/bin/activate
cd indy-tails-server/docker
./manage start 193.138.1.21 --logs
```

```
cd aca-py
source .venv_acapy/bin/activate
aca-py start --arg-file args/user.yaml
```

```
cd aca-py
source .venv_acapy/bin/activate
aca-py start --arg-file args/user.yaml
```

```
cd aca-py
source .venv_acapy/bin/activate
aca-py start --arg-file args/agg.yaml
```

```
cd aca-py
source .venv_acapy/bin/activate
aca-py start --arg-file args/vcs.yaml
```

```
cd aca-py
source .venv_cloudcontroller/bin/activate
cd controllers
python3 controller.py --config config/user_config.py 
```

```
cd aca-py
source .venv_cloudcontroller/bin/activate
cd controllers
python3 controller.py --config config/agg_config.py 
```

```
cd aca-py
source .venv_cloudcontroller/bin/activate
cd controllers
python3 vcs.py --config config/vcs_config.py 
```