class WorkflowHandlerMigration(Exception):
    def __init__(self, new_workflow_handler):
        self.new_workflow_handler = new_workflow_handler

class WorkflowFailure(Exception):
    pass
