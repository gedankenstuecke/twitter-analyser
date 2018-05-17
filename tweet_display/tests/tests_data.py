import os

from django.test import TestCase

from ..read_data import create_main_dataframe
from ..analyse_data import create_heatmap, \
    create_hourly_stats, \
    create_overall, \
    create_timeline, \
    create_top_replies, \
    create_tweet_types


class DataTestCase(TestCase):
    """
    Test cases for data loading and analysis.
    """

    def setUp(self):
        test_file = os.path.join(os.path.dirname(os.path.realpath('__file__')), 'minimized_test_archive.zip')
        self.df = create_main_dataframe(test_file)

    def test_create_hourly_stats(self):
        with self.assertRaises(KeyError):  # KeyError: 'Weekday'
            create_hourly_stats(self.df)

    def test_create_heatmap(self):
        heatmap = create_heatmap(self.df)
        self.assertEquals(heatmap.shape, (0, 2))

    def test_create_overall(self):
        overall = create_overall(self.df)
        self.assertEquals(overall.shape, (62, 2))

    def test_create_timeline(self):
        with self.assertRaises(NotImplementedError):
            create_timeline(self.df)  # NotImplementedError: Not supported for type RangeIndex

    def test_top_replies(self):
        replies = create_top_replies(self.df)
        self.assertEquals(replies.shape, (2, 6))

    def test_top_types(self):
        types = create_tweet_types(self.df)
        self.assertEquals(types.shape, (62, 9))
