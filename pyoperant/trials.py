import logging
from pyoperant import queues, utils

logger = logging.getLogger(__name__)

class Trial(utils.Event):
    """docstring for Trial"""
    def __init__(self,
                 index=None,
                 experiment=None,
                 stimulus_condition=None,
                 *args, **kwargs):

        super(Trial, self).__init__(*args, **kwargs)
        self.label = 'trial'
        self.index = index

        # Object references
        self.experiment = experiment
        self.condition = stimulus_condition

        # Trial statistics
        self.stimulus = None
        self.response = None
        self.correct = None
        self.rt = None
        self.reward = False
        self.punish = False

    def run(self):
        """
        This is where the basic trial structure is encoded. The main structure
        is as follows: Get stimulus -> Initiate trial -> Play stimulus ->
        Receive response ->  Consequate response -> Finish trial -> Save data.
        The stimulus, response and consequate stages are broken into pre, main,
        and post stages. This seems a bit too subdivided, and it may be, but a
        pre and post stage allow for a clean place to put delays between stages.
        """

        self.experiment.this_trial = self

        # Get the stimulus
        # Currently this doesn't allow for any keyword arguments (e.g. replacement, shuffle)
        logger.debug("Getting trial stimulus")
        self.stimulus = self.condition.get()

        # Any pre-trial logging / computations
        logger.debug("Calling trial_pre")
        self.experiment.trial_pre()

        # Perform stimulus playback
        logger.debug("Calling stimulus_pre")
        self.experiment.stimulus_pre()
        logger.debug("Calling stimulus_main")
        self.experiment.stimulus_main()
        logger.debug("Calling stimulus_post")
        self.experiment.stimulus_post()

        # Evaluate subject's response
        logger.debug("Calling response_pre")
        self.experiment.response_pre()
        logger.debug("Calling response_main")
        self.experiment.response_main()
        logger.debug("Calling response_post")
        self.experiment.response_post()

        # Consequate the response with a reward, punishment or neither
        logger.debug("Calling consequate_pre")
        self.experiment.consequate_pre()
        logger.debug("Calling consequate_main")
        self.experiment.consequate_main()
        logger.debug("Calling consequate_post")
        self.experiment.consequate_post()

        # Finalize trial
        logger.debug("Calling trial_post")
        self.experiment.trial_post()

        # Store trial data
        logger.debug("Calling subject store")
        self.experiment.subject.store_data()


class TrialHandler(queues.BaseHandler):

    def __init__(self, block):

        super(TrialHandler, self).__init__(queue=block.queue,
                                           items=block.conditions,
                                           weights=block.weights,
                                           queue_parameters=block.queue_parameters)
        self.block = block
        self.trial_index = 0

    def __iter__(self):

        for condition in self.queue:
            self.trial_index += 1
            logger.debug("Creating trial %d" % self.trial_index)
            trial = Trial(index=self.trial_index,
                          experiment=self.block.experiment,
                          stimulus_condition=condition)
            yield trial
