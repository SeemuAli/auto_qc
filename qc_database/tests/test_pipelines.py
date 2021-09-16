import unittest
from pipeline_monitoring.pipelines import *


class TestGermlinePipeline(unittest.TestCase):



	def test_samplecomplete_func(self):

		'''
		test case: error file deleted in sample directory 19M07251
		'''

		results_dir = 'test_data/TSC_sampletest/IlluminaTruSightCancer'
		sample_names = ['19M06586', '19M07039', '19M07040', '19M07041', '19M07048', '19M07084', '19M07089', '19M07098', '19M07121', '19M07162', '19M07167','19M07173', '19M07203', '19M07234', '19M07248','19M07251', '19M07267', '19M07333', '19M07356', '19M07398', '19M07411', '19M07435', '19M07436'] # add all samples lists 
		run_id = '190520_M02641_0219_000000000-CGJT6'

		germline_enrichment = GermlineEnrichment(results_dir = results_dir,
											sample_names = sample_names,
											run_id = run_id
			)

		sample_complete = germline_enrichment.sample_is_complete('19M07039')
		noerrorfile = germline_enrichment.sample_is_complete('19M07251')

		print(sample_complete)
		self.assertEqual(sample_complete, True)
		self.assertEqual(noerrorfile, False)

 


	def test_samplevalid_func(self):

		'''
		test case: ensure sample valid function work correctly (no intermediate files: '*_rmdup.bam',
										 '*_DepthOfCoverage etc.')
		'''

		results_dir = 'test_data/TSC_sampletest/IlluminaTruSightCancer'
		sample_names = ['19M06586', '19M07039', '19M07040', '19M07041', '19M07048', '19M07084', '19M07089', '19M07098', '19M07121', '19M07162', '19M07167','19M07173', '19M07203', '19M07234', '19M07248','19M07251', '19M07267', '19M07333', '19M07356', '19M07398', '19M07411', '19M07435', '19M07436'] # add all samples lists 
		run_id = '190520_M02641_0219_000000000-CGJT6'
		
		germline_enrichment = GermlineEnrichment(results_dir = results_dir,
											sample_names = sample_names,
											run_id = run_id,
			sample_not_expected_files = ['*_rmdup.bam', '*_DepthOfCoverage'],
			sample_expected_files = ['*.bam',
		 							'*.g.vcf',
		  							'*_AlignmentSummaryMetrics.txt',
		  							'*_Contamination.selfSM',
		  							'*_DepthOfCoverage.gz',
		  							'*_HsMetrics.txt',
		  							'*_InsertMetrics.txt',
		  							'*_MarkDuplicatesMetrics.txt',
		  								'*_QC.txt']
			)

		sample_valid = germline_enrichment.sample_is_valid('19M06586')
		missing_bam = germline_enrichment.sample_is_valid('19M07039') #sample directory missing bam file 
		depthofcov_file = germline_enrichment.sample_is_valid('19M07411') #sample directory contains *_DepthOfCoverage file


		print(sample_valid)

		self.assertEqual(sample_valid, True)
		self.assertEqual(missing_bam, False)
		self.assertEqual(depthofcov_file, False)


	def test_runcomplete_func(self):
