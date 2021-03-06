import pytest
import torch
import baal.bayesian.dropout


def test_1d_eval_remains_stochastic():
    dummy_input = torch.randn(8, 10)
    test_module = torch.nn.Sequential(
        torch.nn.Linear(10, 5),
        torch.nn.ReLU(),
        baal.bayesian.dropout.Dropout(p=0.5),
        torch.nn.Linear(5, 2),
    )
    test_module.eval()
    # NOTE: This is quite a stochastic test...
    torch.manual_seed(2019)
    with torch.no_grad():
        assert not all(
            (test_module(dummy_input) == test_module(dummy_input)).all()
            for _ in range(10)
        )


def test_2d_eval_remains_stochastic():
    dummy_input = torch.randn(8, 1, 5, 5)
    test_module = torch.nn.Sequential(
        torch.nn.Conv2d(1, 1, 1),
        torch.nn.ReLU(),
        baal.bayesian.dropout.Dropout2d(p=0.5),
        torch.nn.Conv2d(1, 1, 1),
    )
    test_module.eval()
    # NOTE: This is quite a stochastic test...
    torch.manual_seed(2019)
    with torch.no_grad():
        assert not all(
            (test_module(dummy_input) == test_module(dummy_input)).all()
            for _ in range(10)
        )


@pytest.mark.parametrize("inplace", (True, False))
def test_patch_module_replaces_all_dropout_layers(inplace):

    test_module = torch.nn.Sequential(
        torch.nn.Linear(10, 5),
        torch.nn.ReLU(),
        torch.nn.Dropout(p=0.5),
        torch.nn.Linear(5, 2),
    )

    mc_test_module = baal.bayesian.dropout.patch_module(test_module, inplace=inplace)

    # objects should be the same if inplace is True and not otherwise:
    assert (mc_test_module is test_module) == inplace
    assert not any(
        isinstance(module, torch.nn.Dropout) for module in mc_test_module.modules()
    )
    assert any(
        isinstance(module, baal.bayesian.dropout.Dropout)
        for module in mc_test_module.modules()
    )


def test_module_class_replaces_dropout_layers():
    dummy_input = torch.randn(8, 10)
    test_module = torch.nn.Sequential(
        torch.nn.Linear(10, 5),
        torch.nn.ReLU(),
        torch.nn.Dropout(p=0.5),
        torch.nn.Linear(5, 2),
    )
    test_mc_module = baal.bayesian.dropout.MCDropoutModule(test_module)

    assert not any(
        isinstance(module, torch.nn.Dropout) for module in test_module.modules()
    )
    assert any(
        isinstance(module, baal.bayesian.dropout.Dropout)
        for module in test_module.modules()
    )
    torch.manual_seed(2019)
    with torch.no_grad():
        assert not all(
            (test_mc_module(dummy_input) == test_mc_module(dummy_input)).all()
            for _ in range(10)
        )
