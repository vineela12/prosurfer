class Module:
    """
    Set class/instance variable hooks to register for events. The following hooks
    are available...

    * pubmsg    - Triggered when a public message is received
    * privmsg   - Triggered when a private message is received
    * join      - Someone /joins the channel
    * part      - Someone /parts the channel
    * topic     - Channel topic changed
    * chanmode  - Channel mode changed
    """

    def __init__(self, config):
        self.config = config

    hooks = []
