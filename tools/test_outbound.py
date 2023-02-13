import yaml
import rule_engine

config = {}
outbound_rules = []


def setup_rules():
    global outbound_rules
    for outbound_rule_config in config["rules"]["outbound"]:
        outbound_rule = {
            "rule": rule_engine.Rule(outbound_rule_config["rule"]),
            "topic": outbound_rule_config["topic"],
            "payload": outbound_rule_config["payload"]
        }
        outbound_rules.append(outbound_rule)


def run():
    with open('config.yaml', 'r') as f:
        global config
        config = yaml.safe_load(f)

    setup_rules()

    events = [
        {
            "event": "button_down"
        },
        {
            "event": "button_up"
        }
    ]

    for event in events:
        outbound_rule = next(
            filter(lambda outbound_rule: outbound_rule["rule"].matches(event), outbound_rules), None)
        if outbound_rule:
            print(
                f'topic: {outbound_rule["topic"]} payload: {outbound_rule["payload"]}')


if __name__ == '__main__':
    run()
