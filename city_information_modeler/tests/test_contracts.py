"""Every core method must declare a usable parallel contract. No network needed."""

import inspect

import pytest

from city_information_modeler.core.conflation import BuildingConflator
from city_information_modeler.core.contracts import (
    ParallelSpec,
    parallel_spec_of,
    parallelizable,
)
from city_information_modeler.core.sources import FOOTPRINT_SOURCES

# Every stateless core class, so the contract is checked for all of them and not only for
# the ones a test author remembered.
CORE_CLASSES = dict(FOOTPRINT_SOURCES, conflator=BuildingConflator)


def public_methods(cls):
    """The methods a caller is expected to use."""
    found = []
    for name, member in inspect.getmembers(cls, predicate=inspect.isfunction):
        if not name.startswith("_"):
            found.append((name, member))
    return found


@pytest.mark.parametrize("source_name,source_class", sorted(FOOTPRINT_SOURCES.items()))
def test_entry_point_declares_a_spec(source_name, source_class):
    spec = parallel_spec_of(source_class.fetch_buildings)
    assert spec is not None, f"{source_name}.fetch_buildings declares no ParallelSpec"
    assert spec.split_arg == "boundary_geojson"


def test_conflation_entry_point_declares_a_spec():
    spec = parallel_spec_of(BuildingConflator.conflate)
    assert spec is not None
    assert spec.split_arg == "source_frames"


@pytest.mark.parametrize("class_name,core_class", sorted(CORE_CLASSES.items()))
def test_declared_split_arg_is_a_real_parameter(class_name, core_class):
    for name, method in public_methods(core_class):
        spec = parallel_spec_of(method)
        if spec is None or spec.split == "none":
            continue
        parameters = inspect.signature(method).parameters
        assert spec.split_arg in parameters, (
            f"{class_name}.{name} declares split_arg {spec.split_arg!r}, "
            f"which is not one of its parameters"
        )


@pytest.mark.parametrize("class_name,core_class", sorted(CORE_CLASSES.items()))
def test_core_classes_are_immutable(class_name, core_class):
    """A stateless core class must not be mutable, or workers could drift apart."""
    instance = core_class()
    first_field = next(iter(instance.__dataclass_fields__))
    with pytest.raises(Exception):
        setattr(instance, first_field, None)


def test_dedup_merge_requires_a_column():
    with pytest.raises(ValueError):
        ParallelSpec(
            split="spatial_tiles",
            merge="concat_dedup",
            workload="io",
            split_arg="boundary_geojson",
        )


def test_unknown_strategies_are_rejected():
    with pytest.raises(ValueError):
        ParallelSpec(split="sideways", merge="concat", workload="io", split_arg="x")
    with pytest.raises(ValueError):
        ParallelSpec(split="row_batches", merge="blend", workload="io", split_arg="x")
    with pytest.raises(ValueError):
        ParallelSpec(split="row_batches", merge="concat", workload="gpu", split_arg="x")


def test_decorator_leaves_the_method_callable():
    """Declaring parallelism must not change what a direct call does."""

    @parallelizable(
        split="row_batches", merge="concat", workload="cpu", split_arg="values"
    )
    def double(values):
        return [value * 2 for value in values]

    assert double([1, 2, 3]) == [2, 4, 6]
    assert parallel_spec_of(double).split == "row_batches"
