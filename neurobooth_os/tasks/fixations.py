# -*- coding: utf-8 -*-
"""
Created on Mon Nov 22 11:24:12 2021

@author: STM
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Nov 22 11:22:32 2021

@author: STM
"""

import os.path as op

import neurobooth_os
from neurobooth_os.tasks.task import Task_Eyetracker
from neurobooth_os.tasks.task import Eyelink_HostPC
from neurobooth_os.tasks import utils


class Fixation_Target(Task_Eyetracker):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def present_task(
        self, prompt=True, duration=3, target_pos=(-10, 5), target_size=0.7, **kwargs
    ):
        self.countdown_to_stimulus()
        self.target.pos = [self.deg_2_pix(target_pos[0]), self.deg_2_pix(target_pos[1])]
        self.target.size = self.deg_2_pix(target_size)  # target_size from deg to cms
        if sum(self.target.size):
            self.send_target_loc(self.target.pos)

        # Send event to eyetracker and to LSL separately
        self.sendMessage(self.marker_task_start, False)
        self.show_text(
            screen=self.target,
            msg="Task",
            audio=None,
            wait_time=duration,
            waitKeys=False,
        )
        self.sendMessage(self.marker_task_end, False)

        if prompt:
            func_kwargs = locals()
            del func_kwargs["self"]
            self.show_text(
                screen=self.press_task_screen,
                msg="Task-continue-repeat",
                func=self.present_task,
                func_kwargs=func_kwargs,
                waitKeys=False,
            )


class Fixation_Target_Multiple(Eyelink_HostPC):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def present_task(
        self,
        prompt=True,
        duration=3,
        trial_pos=[(0, 0), (0, 15)],
        target_size=0.7,
        **kwargs
    ):

        self.sendMessage(self.marker_task_start)
        self.countdown_to_stimulus()

        for pos in trial_pos:
            self.target.pos = [self.deg_2_pix(pos[0]), self.deg_2_pix(pos[1])]
            self.target.size = self.deg_2_pix(
                target_size
            )  # target_size from deg to cms
            if sum(self.target.size):
                self.send_target_loc(self.target.pos)

            # Send event to eyetracker and to LSL separately
            self.sendMessage(self.marker_trial_start, False)
            self.update_screen(self.target.pos[0], self.target.pos[1])
            self.show_text(
                screen=self.target,
                msg="Trial",
                audio=None,
                wait_time=duration,
                waitKeys=False,
            )
            self.sendMessage(self.marker_trial_end, False)

        self.sendMessage(self.marker_task_end)
        self.clear_screen()

        if prompt:
            func_kwargs = locals()
            del func_kwargs["self"]
            self.show_text(
                screen=self.press_task_screen,
                msg="Task-continue-repeat",
                func=self.present_task,
                func_kwargs=func_kwargs,
                waitKeys=False,
            )


class Fixation_Target_sidetrials(Task_Eyetracker):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def present_task(
        self,
        prompt=True,
        duration=3,
        target_pos=(-10, 10),
        target_size=0.7,
        trial_intruct=["trial 1", "trial 2"],
        **kwargs
    ):

        self.sendMessage(self.marker_task_start)

        for nth, trl in enumerate(trial_intruct):
            self.display_trial_instructions(trl)
            self.countdown_to_stimulus()
            self.perform_trial(duration, target_pos, target_size)
            self.present_trial_ended_msg()

        self.sendMessage(self.marker_task_end)

        if prompt:
            func_kwargs = locals()
            del func_kwargs["self"]
            self.show_text(
                screen=self.press_task_screen,
                msg="Task-continue-repeat",
                func=self.present_task,
                func_kwargs=func_kwargs,
                waitKeys=False,
            )

    def perform_trial(self, duration, target_pos, target_size):
        self.calc_target_position_and_size(target_pos, target_size)
        # Send event to eyetracker and to LSL separately
        self.sendMessage(self.marker_trial_start, False)
        self.show_text(
            screen=self.target,
            msg="Trial",
            wait_time=duration,
            abort_keys=self.abort_keys,
            waitKeys=False
        )
        self.sendMessage(self.marker_trial_end, False)

    def present_trial_ended_msg(self):
        msg = utils.create_text_screen(self.win, "Task on one side ended")
        utils.present(self.win, msg, wait_time=2, waitKeys=False)

    def calc_target_position_and_size(self, target_pos, target_size):
        self.target.pos = [
            self.deg_2_pix(target_pos[0]),
            self.deg_2_pix(target_pos[1]),
        ]
        self.target.size = self.deg_2_pix(
            target_size
        )  # target_size from deg to cms
        if sum(self.target.size):
            self.send_target_loc(self.target.pos)

    def display_trial_instructions(self, trl_instructions) -> None:
        """
        Display the instructions for the current trial
        Parameters
        ----------
        trl_instructions str: The instructions for the current trial
        """
        msg = utils.create_text_screen(self.win, trl_instructions + "\n\n\nPress CONTINUE")
        utils.present(self.win, msg)


if __name__ == "__main__":

    t = Fixation_Target_Multiple()
    t.run(duration=3, trial_pos=[(0, 7.5), (15, 7.5), (-15, 0)], target_size=0.7)
