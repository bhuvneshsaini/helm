from dataclasses import dataclass, field
from typing import List

from benchmark.augmentations.perturbation import (
    Perturbation,
    PerturbationSpec,
    create_perturbation,
    CleanPerturbation,
)
from benchmark.scenario import Instance


@dataclass(frozen=True)
class DataAugmenter:

    # Perturbations to use to generate new instances
    perturbations: List[Perturbation]

    # Whether to perturb references
    should_perturb_references: bool

    def generate(self, instances: List[Instance], include_original: bool = True) -> List[Instance]:
        """
        Given a list of Instances, generate a new list of perturbed Instances.
        include_original controls whether to include the original Instance in the new list of Instances.
        """
        perturbations = self.perturbations + [CleanPerturbation()] if include_original else self.perturbations

        result: List[Instance] = []
        for i, instance in enumerate(instances):
            # Tag all the perturbed instances generated from the same instance with the same ID
            id_tag: str = f"id{i}"
            for perturbation in perturbations:
                result.append(perturbation.apply(id_tag, instance, self.should_perturb_references))
        return result


@dataclass(frozen=True)
class DataAugmenterSpec:

    # List of perturbation specs to use to augment the data
    perturbation_specs: List[PerturbationSpec] = field(default_factory=list)

    # Whether to perturb references
    should_perturb_references: bool = False

    # Whether to augment train instances
    should_augment_train_instances: bool = False

    # Whether to include the original instances in the augmented set of train instances
    should_include_original_train: bool = False

    # Whether to augment val/test instances
    should_augment_eval_instances: bool = False

    # Whether to include the original instances in the augmented set of val/test instances
    should_include_original_eval: bool = False

    @property
    def perturbations(self) -> List[Perturbation]:
        return [create_perturbation(spec) for spec in self.perturbation_specs]

    # TODO: Get rid of this after we add the new instance fields:
    #       https://github.com/stanford-crfm/benchmarking/issues/124
    @property
    def tags(self) -> List[str]:
        tags: List[str] = [perturbation.tag for perturbation in self.perturbations]
        if self.should_include_original_eval:
            tags.append(CleanPerturbation.CLEAN_TAG)
        return tags


def create_data_augmenter(data_augmenter_spec: DataAugmenterSpec) -> DataAugmenter:
    """Creates a DataAugmenter from a DataAugmenterSpec."""
    return DataAugmenter(
        perturbations=data_augmenter_spec.perturbations,
        should_perturb_references=data_augmenter_spec.should_perturb_references,
    )
