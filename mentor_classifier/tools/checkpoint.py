import logging
import os

from mentor_classifier.mentor import Mentor
from mentor_classifier.metrics import Metrics
from mentor_classifier.classifiers import checkpoint_path, create_classifier
from mentor_classifier.classifiers import checkpoint_path
from mentor_classifier.classifiers.training import find_classifier_training_factory

logging.basicConfig(level=logging.INFO)

def test() -> None:
    ARCH = os.getenv("ARCH")
    CHECKPOINT = os.getenv("CHECKPOINT")
    CHECKPOINT_ROOT = os.getenv("CHECKPOINT_ROOT") or "/app/checkpoint"
    MENTOR = os.getenv("MENTOR")
    TEST_SET = os.getenv("TEST_SET")
    print(f"ARCH {ARCH}")
    print(f"CHECKPOINT {CHECKPOINT}")
    print(f"MENTOR {MENTOR}")
    classifier = create_classifier(
        checkpoint_root=CHECKPOINT_ROOT, arch=ARCH, checkpoint=CHECKPOINT, mentors=MENTOR
    )
    metrics = Metrics()
    accuracy = metrics.test_accuracy(classifier, TEST_SET)
    print(f"  ARCH {ARCH}")
    print(f"  CHECKPOINT {CHECKPOINT}")
    print(f"  MENTOR {MENTOR}")
    print(f"  ACCURACY: {accuracy}")

def train() -> None:
    ARCH = os.getenv("ARCH")
    CHECKPOINT = os.getenv("CHECKPOINT") or datetime.datetime.now().strftime(
        "%Y-%m-%d-%H%M"
    )
    CHECKPOINT_ROOT = os.getenv("CHECKPOINT_ROOT") or "/app/checkpoint"
    MENTOR_ROOT = os.getenv("MENTOR_ROOT") or "/app/mentors"
    MENTOR = os.getenv("MENTOR")
    logging.info(f"ARCH {ARCH}")
    logging.info(f"CHECKPOINT {CHECKPOINT}")
    logging.info(f"CHECKPOINT_ROOT {CHECKPOINT_ROOT}")
    logging.info(f"MENTOR_ROOT {MENTOR_ROOT}")
    logging.info(f"MENTOR {MENTOR}")
    fac = find_classifier_training_factory(ARCH)
    cp = checkpoint_path(CHECKPOINT_ROOT, ARCH, CHECKPOINT)
    logging.info(f"CHECKPOINT_PATH {cp}")
    mentor_ids = (
        [
            d
            for d in os.listdir(MENTOR_ROOT)
            if os.path.isdir(os.path.join(MENTOR_ROOT, d))
        ]
        if not MENTOR
        else [MENTOR]
    )
    logging.info(f"training mentor list: {mentor_ids}")
    for mentor_id in mentor_ids:
        if not os.path.isdir(MENTOR_ROOT):
            continue
        m = Mentor(mentor_id, MENTOR_ROOT)
        save_path = os.path.join(cp, mentor_id)
        logging.info(f"train mentor {m.mentor_data_path()} to save path {save_path}...")
        training = fac.create(cp, m)
        scores, accuracy = training.train()
        training.save(to_path=save_path)
        logging.info(f"  CHECKPOINT: {cp}")
        logging.info(f"  ACCURACY: {accuracy}")
