import yaml
import rule_engine

config = {}
inbound_rules = []


def setup_rules():
    global inbound_rules

    for inbound_rule_config in config["rules"]["inbound"]:
        inbound_rule = {
            "rule": rule_engine.Rule(inbound_rule_config["rule"]),
            "light_state": inbound_rule_config["light_state"]
        }
        inbound_rules.append(inbound_rule)


def run():
    with open('config.yaml', 'r') as f:
        global config
        config = yaml.safe_load(f)

    setup_rules()

    msg_payload = {"topic": "hermes/asr/stopListening",
                   "payload": {"siteId": "satellite1"}}

    inbound_rule = next(
        filter(lambda inbound_rule: inbound_rule["rule"].matches(msg_payload), inbound_rules), None)
    light_state_tmp = None
    if inbound_rule:
        light_state_tmp = inbound_rule.get("light_state")
    if light_state_tmp:
        light_state = light_state_tmp
        print(light_state)


if __name__ == '__main__':
    run()
