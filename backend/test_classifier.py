from classifier import classify


def test_factual_is_convergent():
    c = classify("What is the capital of France?")
    assert c.label == "convergent"


def test_math_is_convergent():
    c = classify("Calculate the sum of 47 and 89.")
    assert c.label == "convergent"
    assert c.features["has_number"] == 1


def test_brainstorm_is_divergent():
    c = classify("Brainstorm some creative ideas for a birthday party.")
    assert c.label == "divergent"


def test_creative_is_divergent():
    c = classify("Write a short poem about the ocean and imagine new worlds.")
    assert c.label == "divergent"


def test_high_stakes_triggers_warning():
    c = classify("What is the correct dosage of ibuprofen in mg for a child?")
    assert c.label == "convergent"
    assert c.overreliance_risk == "high"
    assert c.warning is not None


def test_divergent_has_low_overreliance():
    c = classify("Suggest some fun weekend activities.")
    assert c.overreliance_risk == "low"


def test_probability_bounds():
    for p in ["", "hi", "What is 2+2?", "Imagine a story " * 10]:
        c = classify(p)
        assert 0.0 <= c.convergent_probability <= 1.0


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
    print("all tests passed")
