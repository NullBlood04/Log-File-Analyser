from langchain.schema import SystemMessage, HumanMessage

# Local imports
from .parent_aiConnector import Connect_AI
from ..AdditionalTools import (
    ERRORFREQUENCY_SYSTEM_PROMPT,
    ERRORFREQUENCY_HUMAN_PROMPT,
)


class ErrorFrequencyAgent(Connect_AI):

    system_prompt = ERRORFREQUENCY_SYSTEM_PROMPT

    human_prompt = ERRORFREQUENCY_HUMAN_PROMPT

    def frequency_prompt(self, error_content):  # type: ignore
        """
        Uses AI to give one line answer on how frequent the time stamps are

        Args:
            frequency_content (str): A string containing list of timestamps in the format MM/DD/YYYY hh:mm:ss (AM/PM)

        Returns:
            str: A string containing one line answer describing the frequency of error levels of a source

        Example:
            >>> frequency_prompt("[<large list of timestamps>]")
            n number of errors in so-and-so days

            >>> frequency_prompt("[<large list of timestamps>]")
            n number of errors in this day m number of errors in that day
        """
        try:
            message = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=(self.human_prompt + error_content)),
            ]
            self.content = self.chat.invoke(message).content
            return self.content
        except Exception as e:
            return f"Something went Wrong: {e}"


if __name__ == "__main__":
    efa = ErrorFrequencyAgent()
    # timeStamp = "['14-03-2025 01:28:38 PM', '15-03-2025 06:58:12 PM', '16-03-2025 10:58:49 PM', '18-03-2025 09:05:37 AM', '19-03-2025 02:52:22 PM', '21-03-2025 12:52:14 PM', '22-03-2025 02:46:57 PM', '23-03-2025 03:04:09 PM', '24-03-2025 04:32:45 PM', '25-03-2025 04:48:12 PM', '27-03-2025 06:00:09 PM', '31-03-2025 08:42:14 PM', '02-04-2025 11:33:27 AM', '03-04-2025 12:08:58 PM', '04-04-2025 05:38:44 PM', '06-04-2025 02:06:12 PM', '07-04-2025 07:59:14 PM', '09-04-2025 11:41:14 AM', '10-04-2025 01:19:27 PM', '11-04-2025 03:35:01 PM', '13-04-2025 03:31:44 PM', '15-04-2025 04:14:50 PM', '17-04-2025 04:20:05 PM', '19-04-2025 05:20:49 PM', '21-04-2025 03:14:37 PM', '22-04-2025 07:48:37 PM', '24-04-2025 10:02:31 AM', '25-04-2025 07:30:38 PM', '27-04-2025 02:26:31 AM', '28-04-2025 06:29:56 AM', '29-04-2025 06:59:22 AM', '30-04-2025 05:04:53 PM', '01-05-2025 09:08:59 PM', '03-05-2025 07:28:12 PM', '05-05-2025 01:43:58 PM', '06-05-2025 07:45:48 PM', '07-05-2025 08:40:45 PM', '11-05-2025 01:07:21 PM', '13-05-2025 10:53:26 AM', '15-05-2025 11:13:39 AM', '17-05-2025 09:48:07 AM', '18-05-2025 10:08:53 AM', '19-05-2025 10:35:03 AM', '20-05-2025 06:20:22 PM', '21-05-2025 08:42:02 PM', '23-05-2025 09:42:21 AM', '24-05-2025 12:50:25 PM', '26-05-2025 11:10:54 PM', '28-05-2025 10:10:44 AM', '29-05-2025 01:12:15 PM', '30-05-2025 01:17:57 PM', '31-05-2025 05:04:29 PM', '02-06-2025 11:36:46 AM', '03-06-2025 11:42:30 AM', '05-06-2025 09:55:27 AM', '08-06-2025 11:34:29 AM', '10-06-2025 09:49:15 AM', '11-06-2025 09:49:29 AM', '12-06-2025 09:59:36 AM', '13-06-2025 10:05:36 AM', '14-06-2025 09:40:00 PM', '16-06-2025 09:41:35 AM', '17-06-2025 10:00:21 AM', '18-06-2025 10:19:07 AM', '19-06-2025 10:19:45 AM']"
    timeStamp = "[]"
    result = efa.frequency_prompt(timeStamp)
    print(result)
