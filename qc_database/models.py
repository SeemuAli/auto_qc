from django.db import models
from django.conf import settings
from qc_analysis.parsers import *

class Instrument(models.Model):
	"""
	Model to hold a sequencer

	"""

	instrument_id = models.CharField(max_length=255, primary_key=True)
	instrument_type = models.CharField(max_length=255)

	def __str__(self):
		return self.instrument_id

class Run(models.Model):
	"""
	A run from a sequencer e.g 190927_D00501_0360_AH5JTVBCX3

	Populated with information from the RunParams and Runinfo files.

	"""

	run_id = models.CharField(max_length=50, primary_key=True)

	instrument = models.ForeignKey(Instrument, on_delete=models.CASCADE, blank=True, null=True)
	instrument_date = models.DateField(blank=True, null=True)
	setup_date = models.DateField(blank=True, null=True)
	samplesheet_date = models.DateField(blank=True, null=True)
	lanes = models.IntegerField(blank=True, null=True)

	investigator = models.CharField(max_length=255, blank=True, null=True)
	experiment = models.CharField(max_length=255, blank=True, null=True)
	chemistry = models.CharField(max_length=255, blank=True, null=True)

	num_reads = models.IntegerField(blank=True, null=True)
	length_read1 = models.IntegerField(blank=True, null=True)
	length_read2 = models.IntegerField(blank=True, null=True)
	num_indexes = models.IntegerField(blank=True, null=True)
	length_index1 = models.IntegerField(blank=True, null=True)
	length_index2 = models.IntegerField(blank=True, null=True)

	def __str__(self):
		return self.run_id


class InteropRunQuality(models.Model):
	"""
	An interop summary file for Illumina 

	"""

	run = models.ForeignKey(Run, on_delete=models.CASCADE)
	read_number = models.IntegerField()
	lane_number = models.IntegerField()
	percent_q30 = models.DecimalField(max_digits=6, decimal_places=3)
	density = models.IntegerField()
	density_pf = models.IntegerField()
	cluster_count = models.IntegerField()
	cluster_count_pf = models.IntegerField()
	error_rate = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True)
	percent_aligned = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True)
	percent_pf = models.DecimalField(max_digits=6, decimal_places=3)
	phasing = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True)
	prephasing = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True)
	reads = models.BigIntegerField()
	reads_pf = models.BigIntegerField()
	yield_g = models.DecimalField(max_digits=10, decimal_places=3)

	def __str__(self):
		return str(self.run.run_id) + '_' + str(self.read_number) + '_' + str(self.lane_number)



class WorkSheet(models.Model):
	"""	
	A worksheet from Shire e.g. 19-5648
	"""

	worksheet_id = models.CharField(max_length=50, primary_key=True)

	def __str__(self):
		return self.worksheet_id

class Sample(models.Model):
	"""
	A sample e.g. 18M13236

	"""

	sample_id = models.CharField(max_length=50, primary_key=True)

	def __str__(self):
		return self.sample_id

	def is_ntc(self):
		"""
		Does the sample name match an ntc pattern.
		"""

		for ntc_marker in ['NTC', 'ntc']:

			if ntc_marker in self.sample_id:

				return True

		return False

class Pipeline(models.Model):
	"""
	A pipeline - should be pipelinename + version

	"""

	pipeline_id = models.CharField(max_length=50, primary_key=True)

	def __str__(self):
		return self.pipeline_id

class AnalysisType(models.Model):
	"""
	An analysis type e.g. IlluminaTruSightCancer

	"""

	analysis_type_id = models.CharField(max_length=50, primary_key=True)

	def __str__(self):
		return self.analysis_type_id

class RunAnalysis(models.Model):
	"""
	A run analysis is a Run object which has been analysed with \
	specific Pipeline and a specific AnalysisType.

	For example 190927_D00501_0360_AH5JTVBCX3 analysed with GermlineEnrichment-2.5.3 on IlluminaTruSightCancer

	"""

	run = models.ForeignKey(Run, on_delete=models.CASCADE)
	start_date = models.DateField(null=True, blank=True)
	pipeline = models.ForeignKey(Pipeline, on_delete=models.CASCADE)
	analysis_type = models.ForeignKey(AnalysisType, on_delete=models.CASCADE)
	results_completed = models.BooleanField(default=False)
	results_valid = models.BooleanField(default=False)
	demultiplexing_completed = models.BooleanField(default=False)
	demultiplexing_valid = models.BooleanField(default=False)
	min_q30_score = models.DecimalField(max_digits=6, decimal_places=3, default=0.8, null=True, blank=True)
	watching = models.BooleanField(default=True)
	manual_approval = models.BooleanField(default=False)
	comment = models.TextField(null=True, blank=True)
	signoff_user = models.ForeignKey('auth.User', on_delete=models.CASCADE, null=True, blank=True, related_name='signoff_user')
	sensitivity = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True)
	sensitivity_lower_ci = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True)
	sensitivity_higher_ci = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True)
	sensitivity_user = models.ForeignKey('auth.User', on_delete=models.CASCADE, null=True, blank=True, related_name='sensitivity_user')
	auto_qc_checks = models.TextField(null=True, blank=True)

	class Meta:
		unique_together = [['run', 'pipeline', 'analysis_type']]

	def __str__(self):
		return self.run.run_id + '_' + self.pipeline.pipeline_id + '_' + self.analysis_type.analysis_type_id

	def get_n_samples_completed(self):

		count = 0

		sample_analyses = SampleAnalysis.objects.filter(run = self.run,
														pipeline = self.pipeline,
														analysis_type = self.analysis_type
														)

		completed = [x.results_completed for x in sample_analyses]

		return completed.count(True), len(completed)


	def get_n_samples_valid(self):

		count = 0

		sample_analyses = SampleAnalysis.objects.filter(run = self.run,
														pipeline = self.pipeline,
														analysis_type = self.analysis_type
														)

		completed = [x.results_valid for x in sample_analyses]

		return completed.count(True), len(completed)


	def passes_run_level_qc(self):

		interop_qualities = InteropRunQuality.objects.filter(run = self.run)

		for interop_quality in interop_qualities:

			if interop_quality.percent_q30 < (self.min_q30_score*100):

				return False

		return True

	def get_ntc_sample(self):

		samples = SampleAnalysis.objects.filter(run = self.run,
												pipeline = self.pipeline,
												analysis_type = self.analysis_type)

		for sample in samples:

			for ntc_marker in ['ntc', 'NTC']:

				if ntc_marker in sample.sample_id:

					return sample

		return None

	def get_worksheets(self):

		worksheets = []

		samples = SampleAnalysis.objects.filter(
			run = self.run,
			pipeline = self.pipeline,
			analysis_type = self.analysis_type
			)

		for sample in samples:

			worksheets.append(sample.worksheet.worksheet_id)

		return '|'.join(list(set(worksheets)))

	def passes_auto_qc(self):
		"""
		Check whether the run analysis passes all QC checks.

		Reads from config file to find out which checks to complete.

		"""

		checks_to_do = self.auto_qc_checks

		if checks_to_do == None:

			return False, 'No Configuration For this Pipeline.'

		checks_to_do = checks_to_do.split(',')

		samples = SampleAnalysis.objects.filter(run = self.run,
												pipeline = self.pipeline,
												analysis_type = self.analysis_type)

		# check is complete and valid

		new_samples_list = []

		if self.demultiplexing_completed == False:

			return False, 'Demultiplexing not complete for some samples'

		if self.demultiplexing_valid == False:

			return False, 'Demultiplexing not valid for some samples'

		if self.results_completed == False:

			return False, 'Run results not completed'

		if self.results_valid == False:

			return False, 'Run results not valid'

		for sample in samples:

			if sample.results_completed == False:

				return False, 'Results not complete for some samples'

			if sample.results_valid == False:

				return False, 'Results not valid for some samples'


			if sample.sample.is_ntc() == False:

				new_samples_list.append(sample)

		if 'pct_q30' in checks_to_do:

			if self.passes_run_level_qc() == False:

				return False, 'Q30 Fail'

		if 'fastqc' in checks_to_do:

			for sample in new_samples_list:

				if sample.passes_fastqc() == False:

					return False, 'FASTQC Fail'

		if 'contamination' in checks_to_do:

			for sample in new_samples_list:

				if sample.passes_contamination() == False:

					return False, 'Contamination Fail'


		if 'ntc_contamination' in checks_to_do:

			for sample in new_samples_list:

				if sample.passes_ntc_contamination() == False:

					return False, 'NTC Contamination Fail'

		if 'sex_match' in checks_to_do:

			for sample in new_samples_list:

				if sample.passes_sex_check() == False:

					return False, 'Sex Match Fail'

		return True, 'All Pass'




class SampleAnalysis(models.Model):
	"""
	A SampleAnalysis object is a Sample analysed on a specific Run with a specific Pipeline on \
	a specific AnalysisType.

	"""

	sample = models.ForeignKey(Sample, on_delete=models.CASCADE)
	run = models.ForeignKey(Run, on_delete=models.CASCADE)
	pipeline = models.ForeignKey(Pipeline, on_delete=models.CASCADE)
	analysis_type = models.ForeignKey(AnalysisType, on_delete=models.CASCADE)
	worksheet = models.ForeignKey(WorkSheet, on_delete=models.CASCADE)
	results_completed = models.BooleanField(default = False)
	results_valid = models.BooleanField(default=False)
	sex = models.CharField(max_length=10, null=True, blank=True)
	contamination_cutoff = models.DecimalField(max_digits=6, decimal_places=3, default=0.15, null=True, blank=True)
	ntc_contamination_cutoff = models.DecimalField(max_digits=6, decimal_places=3, default=10.0, null=True, blank=True)


	class Meta:
		unique_together = [['sample', 'run', 'pipeline', 'analysis_type', 'worksheet']]

	def __str__(self):
		return f'{self.run.run_id}_{self.pipeline.pipeline_id}_{self.analysis_type.analysis_type_id}_{self.sample.sample_id}'

	def passes_fastqc(self):
		"""
		Does the sample have a PASS for the key FASTQC metrics?
		"""

		fastqc_objs = SampleFastqcData.objects.filter(sample_analysis=self)

		if len(fastqc_objs) == 0:

			return None

		for fastqc in fastqc_objs:

			if fastqc.basic_statistics == 'FAIL':

				return False

			elif fastqc.per_base_sequencing_quality == 'FAIL':

				return False

			elif fastqc.per_tile_sequence_quality == 'FAIL': 

				return False

			elif fastqc.per_sequence_quality_scores == 'FAIL': 

				return False

			elif fastqc.per_base_n_content == 'FAIL': 

				return False

		return True

	def get_total_reads(self):

		try:

			hs_metrics_obj = SampleHsMetrics.objects.get(sample_analysis= self)

		except:

			return None

		return hs_metrics_obj.total_reads

	def get_contamination(self):

		try:

			contamination_obj = ContaminationMetrics.objects.get(sample_analysis=self)

		except:

			return 'NA'


		return contamination_obj.freemix

	def passes_contamination(self):

		try:
			contamination_obj = ContaminationMetrics.objects.get(sample_analysis=self)
		except:
			return None

		if contamination_obj.freemix > self.contamination_cutoff:

				return False

		return True

	def passes_ntc_contamination(self):

		run_analysis = RunAnalysis.objects.get(run = self.run,
											pipeline = self.pipeline,
											analysis_type = self.analysis_type
												)

		total_reads = self.get_total_reads()

		if total_reads == None:

			return None

		ntc_obj = run_analysis.get_ntc_sample()

		if self == ntc_obj:

			return 'NA'

		if ntc_obj == None:

			return None

		ntc_reads = ntc_obj.get_total_reads()

		if ntc_reads == None:

			return None

		if (ntc_reads * self.ntc_contamination_cutoff) > total_reads:

			return False


		return True

	def get_sex(self):

		sex = self.sex

		if sex == '0':

			return 'unknown'

		elif sex == '1':

			return 'male'

		elif sex == '2':

			return 'female'

		else:

			return 'NA'


	def get_calculated_sex(self):

		try:
			sex_obj = CalculatedSexMetrics.objects.get(sample_analysis=self)
		except:
			return 'NA'

		return sex_obj.calculated_sex.lower()

	def passes_sex_check(self):

		if self.get_calculated_sex() == self.get_sex():

			return True

		return False

	def get_run_analysis(self):

		try:

			run_analysis = RunAnalysis.objects.get(
				run = self.run,
				pipeline = self.pipeline,
				analysis_type = self.analysis_type
				)

		except:

			return None

		return run_analysis



class SampleFastqcData(models.Model):
	"""
	Model to store data from the FastQC output, there will be one entry per fastq file.
	There is a fastq file made for each lane and each read, so a run will usually have 2-4.
	"""
	sample_analysis = models.ForeignKey(SampleAnalysis, on_delete=models.CASCADE)
	read_number = models.CharField(max_length=10)
	lane = models.CharField(max_length=10)
	basic_statistics = models.CharField(max_length=10)
	per_base_sequencing_quality = models.CharField(max_length=10)
	per_tile_sequence_quality = models.CharField(max_length=10)
	per_sequence_quality_scores = models.CharField(max_length=10)
	per_base_sequence_content = models.CharField(max_length=10)
	per_sequence_gc_content = models.CharField(max_length=10)
	per_base_n_content = models.CharField(max_length=10)
	sequence_length_distribution = models.CharField(max_length=10)
	sequence_duplication_levels = models.CharField(max_length=10)
	overrepresented_sequences = models.CharField(max_length=10)
	adapter_content = models.CharField(max_length=10)
	kmer_content = models.CharField(max_length=10, null=True, blank=True)

	def __str__(self):
		return f'{self.sample_analysis}_{self.read_number}_{self.lane}'

class SampleHsMetrics(models.Model):
	"""
	Model to store output from the Picard HS metrics program.
	One per sample.
	"""

	sample_analysis = models.ForeignKey(SampleAnalysis, on_delete=models.CASCADE)

	bait_set = models.CharField(max_length=255)
	genome_size = models.BigIntegerField(null=True)
	bait_territory = models.BigIntegerField(null=True) 
	target_territory = models.BigIntegerField(null=True)
	bait_design_efficiency = models.DecimalField(max_digits=20, decimal_places=4, null=True)
	total_reads = models.BigIntegerField(null=True)
	pf_reads = models.BigIntegerField(null=True)
	pf_unique_reads = models.BigIntegerField(null=True)
	pct_pf_reads = models.DecimalField(max_digits=20, decimal_places=4, null=True)
	pct_pf_uq_reads = models.DecimalField(max_digits=20, decimal_places=4, null=True)
	pf_uq_reads_aligned = models.IntegerField(null=True)
	pct_pf_uq_reads_aligned = models.DecimalField(max_digits=20, decimal_places=4, null=True) 
	pf_bases_aligned = models.IntegerField(null=True)
	pf_uq_bases_aligned = models.IntegerField(null=True)
	on_bait_bases = models.BigIntegerField(null=True) 
	near_bait_bases = models.BigIntegerField(null=True)
	off_bait_bases = models.BigIntegerField(null=True)
	on_target_bases = models.BigIntegerField(null=True)
	pct_selected_bases = models.DecimalField(max_digits=20, decimal_places=4, null=True)
	pct_off_bait = models.DecimalField(max_digits=20, decimal_places=4, null=True)
	on_bait_vs_selected = models.DecimalField(max_digits=20, decimal_places=4, null=True)
	mean_bait_coverage = models.DecimalField(max_digits=20, decimal_places=4, null=True)
	mean_target_coverage = models.DecimalField(max_digits=20, decimal_places=4, null=True)
	median_target_coverage = models.DecimalField(max_digits=20, decimal_places=4, null=True)
	max_target_coverage = models.DecimalField(max_digits=20, decimal_places=4, null=True)
	pct_usable_bases_on_bait = models.DecimalField(max_digits=20, decimal_places=4, null=True)
	pct_usable_bases_on_target = models.DecimalField(max_digits=20, decimal_places=4, null=True)
	fold_enrichment = models.DecimalField(max_digits=20, decimal_places=4, null=True)
	zero_cvg_targets_pct = models.DecimalField(max_digits=20, decimal_places=4, null=True)
	pct_exc_dupe = models.DecimalField(max_digits=20, decimal_places=4, null=True)
	pct_exc_mapq = models.DecimalField(max_digits=20, decimal_places=4, null=True)
	pct_exc_baseq = models.DecimalField(max_digits=20, decimal_places=4, null=True)
	pct_exc_overlap = models.DecimalField(max_digits=20, decimal_places=4, null=True)
	pct_exc_off_target = models.DecimalField(max_digits=20, decimal_places=4, null=True)
	fold_80_base_penalty = models.DecimalField(max_digits=20, decimal_places=4, null=True)
	pct_target_bases_1x =  models.DecimalField(max_digits=20, decimal_places=4, null=True)
	pct_target_bases_2x = models.DecimalField(max_digits=20, decimal_places=4, null=True)
	pct_target_bases_10x = models.DecimalField(max_digits=20, decimal_places=4, null=True)
	pct_target_bases_20x = models.DecimalField(max_digits=20, decimal_places=4, null=True)
	pct_target_bases_30x = models.DecimalField(max_digits=20, decimal_places=4, null=True)
	pct_target_bases_40x = models.DecimalField(max_digits=20, decimal_places=4, null=True)
	pct_target_bases_50x = models.DecimalField(max_digits=20, decimal_places=4, null=True)
	pct_target_bases_100x = models.DecimalField(max_digits=20, decimal_places=4, null=True)
	hs_library_size = models.DecimalField(max_digits=20, decimal_places=4, null=True)
	hs_penalty_10x = models.DecimalField(max_digits=20, decimal_places=4, null=True) 
	hs_penalty_20x = models.DecimalField(max_digits=20, decimal_places=4, null=True)
	hs_penalty_30x = models.DecimalField(max_digits=20, decimal_places=4, null=True)
	hs_penalty_40x = models.DecimalField(max_digits=20, decimal_places=4, null=True)
	hs_penalty_50x = models.DecimalField(max_digits=20, decimal_places=4, null=True)
	hs_penalty_100x = models.DecimalField(max_digits=20, decimal_places=4, null=True)
	at_dropout = models.DecimalField(max_digits=20, decimal_places=4, null=True)
	gc_dropout = models.DecimalField(max_digits=20, decimal_places=4, null=True)
	het_snp_sensitivity = models.DecimalField(max_digits=20, decimal_places=4, null=True)
	het_snp_q = models.IntegerField(null=True) 

	def __str__(self):
		return str(self.sample_analysis)


class SampleDepthofCoverageMetrics(models.Model):
	"""
	Model for GATK DepthOfCoverage summary metrics

	"""

	sample_analysis = models.ForeignKey(SampleAnalysis, on_delete=models.CASCADE)
	total = models.BigIntegerField()
	mean = models.DecimalField(max_digits=20, decimal_places=4, null=True)
	granular_first_quartile = models.IntegerField()
	granular_median = models.IntegerField()
	granular_third_quartile = models.IntegerField()
	pct_bases_above_20  = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True)
	pct_bases_above_250 = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True)
	pct_bases_above_500 = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True)

	def __str__(self):
		return str(self.sample_analysis)

class DuplicationMetrics(models.Model):
	"""
	Metrics from the MarkDuplicates program.

	"""

	sample_analysis = models.ForeignKey(SampleAnalysis, on_delete=models.CASCADE)
	library = models.CharField(max_length=255)
	unpaired_reads_examined = models.IntegerField()
	read_pairs_examined = models.BigIntegerField()
	secondary_or_supplementary_rds = models.IntegerField()
	unmapped_reads = models.IntegerField()
	unpaired_read_duplicates = models.IntegerField()
	read_pair_duplicates = models.IntegerField()
	read_pair_optical_duplicates = models.IntegerField()
	percent_duplication = models.DecimalField(max_digits=20, decimal_places=4, null=True)
	estimated_library_size = models.BigIntegerField(null=True)

	def __str__(self):
		return str(self.sample_analysis)


class ContaminationMetrics(models.Model):
	"""
	Metrics from the Contamination program
	"""

	sample_analysis = models.ForeignKey(SampleAnalysis, on_delete=models.CASCADE)
	num_snps = models.IntegerField()
	num_reads = models.IntegerField()
	avg_dp = models.DecimalField(max_digits=20, decimal_places=4)
	freemix = models.DecimalField(max_digits=20, decimal_places=4)
	freelk1 = models.DecimalField(max_digits=20, decimal_places=4)
	freelk0 = models.DecimalField(max_digits=20, decimal_places=4)

	def __str__(self):
		return str(self.sample_analysis)

class CalculatedSexMetrics(models.Model):
	"""
	Store the calculated sex
	"""

	sample_analysis = models.ForeignKey(SampleAnalysis, on_delete=models.CASCADE)
	calculated_sex = models.CharField(max_length=10)

	def __str__(self):
		return str(self.sample_analysis)

class AlignmentMetrics(models.Model):
	"""
	Store alignment metrics

	"""

	sample_analysis = models.ForeignKey(SampleAnalysis, on_delete=models.CASCADE)
	category = models.CharField(max_length=16)
	total_reads = models.BigIntegerField()
	pf_reads = models.BigIntegerField()
	pct_pf_reads = models.DecimalField(max_digits=6, decimal_places=4)
	pf_noise_reads = models.IntegerField()
	pf_reads_aligned = models.BigIntegerField()
	pct_pf_reads_aligned = models.DecimalField(max_digits=6, decimal_places=4)
	pf_aligned_bases = models.BigIntegerField()
	pf_hq_aligned_reads = models.BigIntegerField()
	pf_hq_aligned_bases = models.BigIntegerField()
	pf_hq_aligned_q20_bases = models.BigIntegerField()
	pf_hq_median_mismatches = models.IntegerField()
	pf_mismatch_rate = models.DecimalField(max_digits=6, decimal_places=4)
	pf_hq_error_rate = models.DecimalField(max_digits=6, decimal_places=4)
	pf_indel_rate = models.DecimalField(max_digits=6, decimal_places=4)
	mean_read_length = models.DecimalField(max_digits=20, decimal_places=4)
	reads_aligned_in_pairs = models.BigIntegerField()
	pct_reads_aligned_in_pairs = models.DecimalField(max_digits=6, decimal_places=4)
	pf_reads_improper_pairs = models.IntegerField()
	pct_pf_reads_improper_pairs = models.DecimalField(max_digits=6, decimal_places=4)
	bad_cycles = models.IntegerField()
	strand_balance = models.DecimalField(max_digits=6, decimal_places=4)
	pct_chimeras = models.DecimalField(max_digits=6, decimal_places=4)
	pct_adapter = models.DecimalField(max_digits=6, decimal_places=4)

	def __str__(self):
		return str(self.sample_analysis) + '_' + self.category


class VariantCallingMetrics(models.Model):
	"""
	Store variant calling detail metrics

	"""

	sample_analysis = models.ForeignKey(SampleAnalysis, on_delete=models.CASCADE)
	het_homvar_ratio = models.DecimalField(max_digits=7, decimal_places=3)
	pct_gq0_variants = models.DecimalField(max_digits=6, decimal_places=3)
	total_gq0_variants  = models.IntegerField()
	total_het_depth = models.BigIntegerField()
	total_snps = models.IntegerField()
	num_in_db_snp = models.IntegerField()
	novel_snps = models.IntegerField()
	filtered_snps = models.IntegerField()
	pct_dbsnp = models.DecimalField(max_digits=6, decimal_places=3)
	dbsnp_titv = models.DecimalField(max_digits=7, decimal_places=3)
	novel_titv = models.DecimalField(max_digits=7, decimal_places=3)
	total_indels = models.IntegerField()
	novel_indels = models.IntegerField()
	filtered_indels = models.IntegerField()
	pct_dbsnp_indels = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True)
	num_in_db_snp_indels = models.IntegerField()
	dbsnp_ins_del_ratio = models.DecimalField(max_digits=6, decimal_places=3)
	novel_ins_del_ratio = models.DecimalField(max_digits=6, decimal_places=3)
	total_multiallelic_snps = models.IntegerField()
	num_in_db_snp_multiallelic = models.IntegerField()
	total_complex_indels = models.IntegerField()
	num_in_db_snp_complex_indels = models.IntegerField()
	snp_reference_bias = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True)
	num_singletons = models.IntegerField()

	def __str__(self):
		return str(self.sample_analysis)

class InsertMetrics(models.Model):
	"""
	Store insert metrics

	"""

	sample_analysis = models.ForeignKey(SampleAnalysis, on_delete=models.CASCADE)
	mode_insert_size = models.IntegerField(null=True, blank=True) 
	median_insert_size = models.IntegerField()
	median_absolute_deviation = models.IntegerField()
	min_insert_size = models.IntegerField()
	max_insert_size = models.BigIntegerField()
	mean_insert_size = models.DecimalField(max_digits=10, decimal_places=3)
	standard_deviation = models.DecimalField(max_digits=10, decimal_places=3)
	read_pairs = models.BigIntegerField()
	pair_orientation = models.CharField(max_length=3)
	width_of_10_percent = models.IntegerField(null=True, blank=True)
	width_of_20_percent = models.IntegerField(null=True, blank=True)
	width_of_30_percent = models.IntegerField(null=True, blank=True)
	width_of_40_percent = models.IntegerField(null=True, blank=True)
	width_of_50_percent = models.IntegerField(null=True, blank=True)
	width_of_60_percent = models.IntegerField(null=True, blank=True)
	width_of_70_percent = models.IntegerField(null=True, blank=True)
	width_of_80_percent = models.IntegerField(null=True, blank=True)
	width_of_90_percent = models.IntegerField(null=True, blank=True)
	width_of_95_percent = models.IntegerField(null=True, blank=True)
	width_of_99_percent = models.IntegerField(null=True, blank=True)

	def __str__(self):
		return str(self.sample_analysis)












