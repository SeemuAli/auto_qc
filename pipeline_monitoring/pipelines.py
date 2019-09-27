from pathlib import Path
import glob
from qc_analysis.parsers import *


class GermlineEnrichment:


	def __init__(self, results_dir, sample_names, run_id):


		self.results_dir = results_dir
		self.sample_names = sample_names
		self.run_id = run_id
		self.sample_complete_marker = '1_GermlineEnrichment.sh.e*'
		self.run_complete_marker = '2_GermlineEnrichment.sh.e*'

		self.sample_expected_files = ['*.bam',
		 							'*.g.vcf',
		  							'*_AlignmentSummaryMetrics.txt',
		  							'*_Contamination.selfSM',
		  							'*_DepthOfCoverage.gz',
		  							'*_HsMetrics.txt',
		  							'*_InsertMetrics.txt',
		  							'*_MarkDuplicatesMetrics.txt',
		  							'*_QC.txt']

		self.sample_not_expected_files = ['*_rmdup.bam',
										 '*_DepthOfCoverage']

		self.run_expected_files = ['*_filtered_annotated_roi.vcf',
									'*_filtered_annotated_roi_noMT.vcf',
									'*_pedigree.ped',
									'*_CollectVariantCallingMetrics.txt.variant_calling_detail_metrics',
									'*_CollectVariantCallingMetrics.txt.variant_calling_summary_metrics',
									'*_ExomeDepth_Metrics.txt',
									'*_relatedness.relatedness2',
									'combined_QC.txt',
									'*_cnvReport.csv']


		self.run_not_expected_files =['*_variants_filtered.vcf',
									'BAMs.list']

	def sample_is_complete(self, sample):
		"""	
		Look for presence of file indicating that a sample has completed the pipeline.

		For example the output error log.
		"""	

		results_path = Path(self.results_dir)

		sample_path = results_path.joinpath(sample)

		marker = sample_path.glob(self.sample_complete_marker)

		if len(list(marker)) == 1:

			return True

		return False

	def sample_is_valid(self, sample):
		"""
		Look for files which have to be present for a sample level pipeline to have completed \
		correctly.

		Look for file which if present indicate the pipeline has not finished correctly e.g. intermediate files.
		"""

		results_path = Path(self.results_dir)

		sample_path = results_path.joinpath(sample)

		# check files we want to be there are there
		for file in self.sample_expected_files:

			found_file = sample_path.glob(file)

			if len(list(found_file)) != 1:

				return False

		# check file we do not want to be there are not there
		for file in self.sample_not_expected_files:

			found_file = sample_path.glob(file)

			if len(list(found_file)) > 0:

				return False			

		return True


	def run_is_complete(self):
		"""	
		Look for presence of file indicating that a sample has completed the pipeline.

		For example the output error log.
		"""	

		results_path = Path(self.results_dir)

		marker = results_path.glob(self.run_complete_marker)

		if len(list(marker)) == 1:

			return True

		return False

	def run_is_valid(self):
		"""
		Look for files which have to be present for a run level pipeline to have completed \
		correctly.

		Look for files which if present indicate the pipeline has not finished correctly e.g. intermediate files.
		"""

		results_path = Path(self.results_dir)

		# check files we want to be there are there
		for file in self.run_expected_files:

			found_file = results_path.glob(file)

			if len(list(found_file)) != 1:

				return False

		# check file we do not want to be there are not there
		for file in self.run_not_expected_files:

			found_file = results_path.glob(file)

			if len(list(found_file)) > 0:

				return False			

		return True

	def run_and_samples_complete(self):
		"""
		Return True if all samples are complete and valid and the run
		level is complete and valid. Otherwise return False.

		"""

		# sample level
		for sample in self.sample_names:

			if self.sample_is_complete(sample) == False:

				return False

		# run level
		if self.run_is_complete() == False:

			return False

		return True

	def run_and_samples_valid(self):

		# sample level
		for sample in self.sample_names:

			if self.sample_is_valid(sample) == False:

				return False

		# run level
		if self.run_is_valid() == False:

			return False

		return True	

	def get_fastqc_data(self):

		fastqc_dict = {}

		results_path = Path(self.results_dir)

		for sample in self.sample_names:

			fastqc_data_files = results_path.joinpath(sample).glob(f'*{sample}*_fastqc.txt')

			sample_fastqc_list = []

			for fastqc_data in fastqc_data_files:

				file = fastqc_data.name
				read_number = file.split('_')[-2]
				lane = file.split('_')[-3]

				parsed_fastqc_data = parse_fastqc_file(fastqc_data)

				file_fastqc_dict = {} 
				file_fastqc_dict['lane'] = lane
				file_fastqc_dict['read_number'] = read_number
				file_fastqc_dict['basic_statistics'] = parsed_fastqc_data['Basic Statistics']
				file_fastqc_dict['per_tile_sequence_quality'] = parsed_fastqc_data['Per tile sequence quality']
				file_fastqc_dict['per_base_sequencing_quality'] = parsed_fastqc_data['Per base sequence quality']
				file_fastqc_dict['per_sequence_quality_scores'] = parsed_fastqc_data['Per sequence quality scores']
				file_fastqc_dict['per_base_sequence_content'] = parsed_fastqc_data['Per base sequence content']
				file_fastqc_dict['per_sequence_gc_content'] = parsed_fastqc_data['Per sequence GC content']
				file_fastqc_dict['per_base_n_content'] = parsed_fastqc_data['Per base N content']
				file_fastqc_dict['per_base_sequence_content'] = parsed_fastqc_data['Per base sequence content']
				file_fastqc_dict['sequence_length_distribution'] = parsed_fastqc_data['Sequence Length Distribution']
				file_fastqc_dict['sequence_duplication_levels'] = parsed_fastqc_data['Sequence Duplication Levels']
				file_fastqc_dict['overrepresented_sequences'] = parsed_fastqc_data['Overrepresented sequences']
				file_fastqc_dict['adapter_content'] = parsed_fastqc_data['Adapter Content']
				file_fastqc_dict['kmer_content'] = parsed_fastqc_data['Kmer Content']

				sample_fastqc_list.append(file_fastqc_dict)

			fastqc_dict[sample] = sample_fastqc_list


		return fastqc_dict


	def get_hs_metrics(self):

		results_path = Path(self.results_dir)

		run_hs_metrics_dict = {}

		for sample in self.sample_names:

			hs_metrics_file = results_path.joinpath(sample).glob(f'*{sample}*_HsMetrics.txt')

			hs_metrics_file = list(hs_metrics_file)[0]

			parsed_hs_metrics_data  = parse_hs_metrics_file(hs_metrics_file)

			run_hs_metrics_dict[sample] = parsed_hs_metrics_data

		return run_hs_metrics_dict

	def get_depth_metrics(self):

		results_path = Path(self.results_dir)

		run_depth_metrics_dict = {}

		for sample in self.sample_names:

			sample_depth_summary_file = results_path.joinpath(sample).glob(f'*{sample}*_DepthOfCoverage.sample_summary')

			sample_depth_summary_file = list(sample_depth_summary_file)[0]	

			parsed_depth_metrics = parse_gatk_depth_summary_file(sample_depth_summary_file)

			run_depth_metrics_dict[sample] = parsed_depth_metrics

		return run_depth_metrics_dict

	def get_duplication_metrics(self):

		results_path = Path(self.results_dir)

		run_duplication_metrics_dict = {}

		for sample in self.sample_names:

			sample_duplication_metrics_file = results_path.joinpath(sample).glob(f'*{sample}*_MarkDuplicatesMetrics.txt')

			sample_duplication_metrics_file = list(sample_duplication_metrics_file)[0]	

			parsed_duplication_metrics = parse_duplication_metrics_file(sample_duplication_metrics_file)

			run_duplication_metrics_dict[sample] = parsed_duplication_metrics

		return run_duplication_metrics_dict

	def get_contamination(self):

		results_path = Path(self.results_dir)

		run_contamination_metrics_dict = {}

		for sample in self.sample_names:

			sample_contamination_metrics_file = results_path.joinpath(sample).glob(f'*{sample}*_Contamination.selfSM')

			sample_contamination_metrics_file = list(sample_contamination_metrics_file)[0]	

			parsed_contamination_metrics = parse_contamination_metrics(sample_contamination_metrics_file)

			run_contamination_metrics_dict[sample] = parsed_contamination_metrics

		return run_contamination_metrics_dict


	def get_calculated_sex(self):

		results_path = Path(self.results_dir)

		calculated_sex_dict = {}

		for sample in self.sample_names:

			qc_metrics_file = results_path.joinpath(sample).glob(f'*{sample}*_QC.txt')

			qc_metrics_file = list(qc_metrics_file)[0]

			parsed_qc_metrics_file = parse_qc_metrics_file(qc_metrics_file)

			calculated_sex_dict[sample] = parsed_qc_metrics_file

		return calculated_sex_dict

	def get_alignment_metrics(self):

		results_path = Path(self.results_dir)

		alignment_metrics_dict = {}

		for sample in self.sample_names:

			alignment_metrics_file = results_path.joinpath(sample).glob(f'*{sample}*_AlignmentSummaryMetrics.txt')

			alignment_metrics_file = list(alignment_metrics_file)[0]

			parsed_alignment_metrics_file = parse_alignment_metrics_file(alignment_metrics_file)

			alignment_metrics_dict[sample] = parsed_alignment_metrics_file

		return alignment_metrics_dict

	def get_variant_calling_metrics(self):

		results_path = Path(self.results_dir)

		variant_metrics_dict = {}

		variant_detail_metrics_file = results_path.glob(f'*{self.run_id}*_CollectVariantCallingMetrics.txt.variant_calling_detail_metrics')

		variant_detail_metrics_file = list(variant_detail_metrics_file)[0]

		variant_metrics_dict = parse_variant_detail_metrics_file(variant_detail_metrics_file)

		return variant_metrics_dict


	def get_insert_metrics(self):

		results_path = Path(self.results_dir)

		insert_metrics_dict = {}

		for sample in self.sample_names:

			insert_metrics_file = results_path.joinpath(sample).glob(f'*{sample}*_InsertMetrics.txt')

			insert_metrics_file = list(insert_metrics_file)[0]

			parsed_insert_metrics_file = parse_insert_metrics_file(insert_metrics_file)

			insert_metrics_dict[sample] = parsed_insert_metrics_file

		return insert_metrics_dict


class IlluminaQC:

	def __init__(self,
	 			fastq_dir,
	  			results_dir,
				sample_names,
				n_lanes,
				run_id,
				min_fastq_size=10000000,
				ntc_patterns = ['NTC', 'ntc'],
				run_complete_marker = '1_IlluminaQC.sh.e*',
				copy_complete_marker = '*.variables'):

		self.fastq_dir = fastq_dir
		self.results_dir = results_dir
		self.sample_names = sample_names
		self.n_lanes = n_lanes
		self.run_id = run_id
		self.run_complete_marker = run_complete_marker
		self.min_fastq_size = min_fastq_size
		self.ntc_patterns = ntc_patterns
		self.copy_complete_marker = copy_complete_marker

	def demultiplex_run_is_complete(self):

		results_path = Path(self.fastq_dir)

		marker = results_path.glob(self.run_complete_marker)

		if len(list(marker)) == 1:

			return True

		return False

	def demultiplex_run_is_valid(self):

		fastq_data_path = Path(self.fastq_dir)

		fastq_data_path = fastq_data_path.joinpath('Data')

		for sample in self.sample_names:

			is_negative_control = False

			for pattern in self.ntc_patterns:

				if pattern in sample:

					is_negative_control = True
					break

			sample_fastq_path = fastq_data_path.joinpath(sample)

			# check fastqs created
			for lane in range(1,self.n_lanes+1):


				fastq_r1 = sample_fastq_path.glob(f'{sample}*L00{lane}_R1_001.fastq.gz')
				fastq_r2 = sample_fastq_path.glob(f'{sample}*L00{lane}_R2_001.fastq.gz')
				variables = sample_fastq_path.glob(f'{sample}.variables')

				if len(list(fastq_r1)) != 1:

					return False

				elif len(list(fastq_r2)) != 1:

					return False

				elif len(list(variables)) != 1:

					return False

				fastq_r1 = sample_fastq_path.glob(f'{sample}*L00{lane}_R1_001.fastq.gz')
				fastq_r2 = sample_fastq_path.glob(f'{sample}*L00{lane}_R2_001.fastq.gz')
				
				fastq_r1 = list(fastq_r1)[0]
				fastq_r2 = list(fastq_r2)[0]

				if fastq_r1.stat().st_size < self.min_fastq_size and is_negative_control == False:

					return False

				elif fastq_r2.stat().st_size < self.min_fastq_size  and is_negative_control == False:

					return False


		return True


	def pipeline_copy_complete(self):

		results_data_path = Path(self.results_dir)

		for sample in self.sample_names:

			sample_results_path = results_data_path.joinpath(sample)

			variables_file = sample_results_path.joinpath(self.copy_complete_marker)

			variables_file = glob.glob(str(variables_file))

			if len(variables_file) != 1:

				return False

		return True


class SomaticEnrichment:


	def __init__(self, results_dir, sample_names, run_id, ntc_patterns = ['NTC', 'ntc']):


		self.results_dir = results_dir
		self.sample_names = sample_names
		self.run_id = run_id
		self.ntc_patterns = ntc_patterns
		self.sample_complete_marker = '1_SomaticEnrichment.sh.e*'
		self.run_complete_markers = ['1_cnvkit.sh.e*', '2_cnvkit.sh.e*']

		self.sample_expected_files = ['*_VariantReport.txt',
									'*.bam',
									'*_AlignmentSummaryMetrics.txt',
									'*_DepthOfCoverage.sample_summary',
									'*_QC.txt',
									'*_filteredStrLeftAligned_annotated.vcf',
									'hotspot_variants',
									'hotspot_coverage_135x'
									]

		self.sample_not_expected_files = []

		self.run_sample_expected_files = ['CNVKit/*_common.vcf']
		self.run_expected_files = ['combined_QC.txt', 'samplesCNVKit.txt']

		self.run_not_expected_files =['*.bed']

	def sample_is_complete(self, sample):
		"""	
		Look for presence of file indicating that a sample has completed the pipeline.

		For example the output error log.
		"""	

		results_path = Path(self.results_dir)

		sample_path = results_path.joinpath(sample)

		marker = sample_path.glob(self.sample_complete_marker)

		if len(list(marker)) == 1:

			return True

		return False

	def sample_is_valid(self, sample):
		"""
		Look for files which have to be present for a sample level pipeline to have completed \
		correctly.

		Look for file which if present indicate the pipeline has not finished correctly e.g. intermediate files.
		"""

		results_path = Path(self.results_dir)

		sample_path = results_path.joinpath(sample)

		# check files we want to be there are there
		for file in self.sample_expected_files:

			found_file = sample_path.glob(file)

			if len(list(found_file)) != 1:

				return False

		# check file we do not want to be there are not there
		for file in self.sample_not_expected_files:

			found_file = sample_path.glob(file)

			if len(list(found_file)) > 0:

				return False			

		return True

	def run_is_complete(self):
		"""	
		Check everyone except NTC has the CNV logs
		"""	

		results_path = Path(self.results_dir)

		for sample in self.sample_names:

			skip_sample = False

			for ntc in self.ntc_patterns:

				if ntc in sample:

					skip_sample = True
					break

			if skip_sample == True:

				continue

			for marker in self.run_complete_markers:

				globbed_marker = results_path.joinpath(sample).glob(marker)

		
				if len(list(globbed_marker)) < 1:

					return False

		return True

	def run_is_valid(self):
		"""
		Look for files which have to be present for a run level pipeline to have completed \
		correctly.

		Look for files which if present indicate the pipeline has not finished correctly e.g. intermediate files.
		"""


		results_path = Path(self.results_dir)

		for sample in self.sample_names:

			skip_sample = False

			for ntc in self.ntc_patterns:

				if ntc in sample:

					skip_sample = True
					break

			if skip_sample == True:

				continue

			for file in self.run_sample_expected_files:

				found_file = results_path.joinpath(sample).glob(file)

				if len(list(found_file)) != 1:

					return False

		for file in self.run_expected_files:

			found_file = results_path.glob(file)

			if len(list(found_file)) != 1:

				return False

		# check file we do not want to be there are not there
		for file in self.run_not_expected_files:

			found_file = results_path.glob(file)

			if len(list(found_file)) > 0:

				return False			

		return True


	def run_and_samples_complete(self):
			"""
			Return True if all samples are complete and valid and the run
			level is complete and valid. Otherwise return False.

			"""

			# sample level
			for sample in self.sample_names:

				if self.sample_is_complete(sample) == False:

					return False

			# run level
			if self.run_is_complete() == False:

				return False

			return True


	def run_and_samples_valid(self):

		# sample level
		for sample in self.sample_names:

			if self.sample_is_valid(sample) == False:

				return False

		# run level
		if self.run_is_valid() == False:

			return False

		return True	


	def get_fastqc_data(self):

			fastqc_dict = {}

			results_path = Path(self.results_dir)

			for sample in self.sample_names:

				fastqc_data_files = results_path.joinpath(sample, 'FASTQC').glob(f'*{sample}*_fastqc.txt')

				sample_fastqc_list = []

				for fastqc_data in fastqc_data_files:

					file = fastqc_data.name
					read_number = file.split('_')[-2]
					lane = file.split('_')[-3]

					parsed_fastqc_data = parse_fastqc_file(fastqc_data)

					file_fastqc_dict = {} 
					file_fastqc_dict['lane'] = lane
					file_fastqc_dict['read_number'] = read_number
					file_fastqc_dict['basic_statistics'] = parsed_fastqc_data['Basic Statistics']
					file_fastqc_dict['per_tile_sequence_quality'] = parsed_fastqc_data['Per tile sequence quality']
					file_fastqc_dict['per_base_sequencing_quality'] = parsed_fastqc_data['Per base sequence quality']
					file_fastqc_dict['per_sequence_quality_scores'] = parsed_fastqc_data['Per sequence quality scores']
					file_fastqc_dict['per_base_sequence_content'] = parsed_fastqc_data['Per base sequence content']
					file_fastqc_dict['per_sequence_gc_content'] = parsed_fastqc_data['Per sequence GC content']
					file_fastqc_dict['per_base_n_content'] = parsed_fastqc_data['Per base N content']
					file_fastqc_dict['per_base_sequence_content'] = parsed_fastqc_data['Per base sequence content']
					file_fastqc_dict['sequence_length_distribution'] = parsed_fastqc_data['Sequence Length Distribution']
					file_fastqc_dict['sequence_duplication_levels'] = parsed_fastqc_data['Sequence Duplication Levels']
					file_fastqc_dict['overrepresented_sequences'] = parsed_fastqc_data['Overrepresented sequences']
					file_fastqc_dict['adapter_content'] = parsed_fastqc_data['Adapter Content']
					sample_fastqc_list.append(file_fastqc_dict)

				fastqc_dict[sample] = sample_fastqc_list


			return fastqc_dict

	def get_hs_metrics(self):

		results_path = Path(self.results_dir)

		run_hs_metrics_dict = {}

		for sample in self.sample_names:

			hs_metrics_file = results_path.joinpath(sample).glob(f'*{sample}*_HsMetrics.txt')

			hs_metrics_file = list(hs_metrics_file)[0]

			parsed_hs_metrics_data  = parse_hs_metrics_file(hs_metrics_file)

			run_hs_metrics_dict[sample] = parsed_hs_metrics_data

		return run_hs_metrics_dict

	def get_depth_metrics(self):

		results_path = Path(self.results_dir)

		run_depth_metrics_dict = {}

		for sample in self.sample_names:

			sample_depth_summary_file = results_path.joinpath(sample).glob(f'*{sample}*_DepthOfCoverage.sample_summary')

			sample_depth_summary_file = list(sample_depth_summary_file)[0]	

			parsed_depth_metrics = parse_gatk_depth_summary_file(sample_depth_summary_file)

			run_depth_metrics_dict[sample] = parsed_depth_metrics

		return run_depth_metrics_dict


	def get_duplication_metrics(self):

		results_path = Path(self.results_dir)

		run_duplication_metrics_dict = {}

		for sample in self.sample_names:

			sample_duplication_metrics_file = results_path.joinpath(sample).glob(f'*{sample}*_markDuplicatesMetrics.txt')

			sample_duplication_metrics_file = list(sample_duplication_metrics_file)[0]	

			parsed_duplication_metrics = parse_duplication_metrics_file(sample_duplication_metrics_file)

			run_duplication_metrics_dict[sample] = parsed_duplication_metrics

		return run_duplication_metrics_dict


	def get_calculated_sex(self):

		results_path = Path(self.results_dir)

		calculated_sex_dict = {}

		for sample in self.sample_names:

			qc_metrics_file = results_path.joinpath(sample).glob(f'*{sample}*_QC.txt')

			qc_metrics_file = list(qc_metrics_file)[0]

			parsed_qc_metrics_file = parse_qc_metrics_file(qc_metrics_file)

			calculated_sex_dict[sample] = parsed_qc_metrics_file

		return calculated_sex_dict


	def get_alignment_metrics(self):

		results_path = Path(self.results_dir)

		alignment_metrics_dict = {}

		for sample in self.sample_names:

			alignment_metrics_file = results_path.joinpath(sample).glob(f'*{sample}*_AlignmentSummaryMetrics.txt')

			alignment_metrics_file = list(alignment_metrics_file)[0]

			parsed_alignment_metrics_file = parse_alignment_metrics_file(alignment_metrics_file)

			alignment_metrics_dict[sample] = parsed_alignment_metrics_file

		return alignment_metrics_dict

	def get_insert_metrics(self):

		results_path = Path(self.results_dir)

		insert_metrics_dict = {}

		for sample in self.sample_names:

			insert_metrics_file = results_path.joinpath(sample).glob(f'*{sample}*_InsertMetrics.txt')

			insert_metrics_file = list(insert_metrics_file)[0]

			parsed_insert_metrics_file = parse_insert_metrics_file(insert_metrics_file)

			insert_metrics_dict[sample] = parsed_insert_metrics_file

		return insert_metrics_dict