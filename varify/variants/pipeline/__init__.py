from varify.pipeline import Channel

VARIANT_CHANNEL = Channel('variants', ['manifest_path', 'database'])


# Setup local handlers to watch the channels of interest..
from varify.samples.pipeline import SAMPLE_CHANNEL
from . import handlers
handlers.load_variants.watch(SAMPLE_CHANNEL)
handlers.load_effects.watch(VARIANT_CHANNEL)
