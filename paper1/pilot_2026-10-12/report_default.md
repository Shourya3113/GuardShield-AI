# Paired audit report: `pilot_obf`

Dataset `2fa986936fec6ed6`, commit `0aa9019358b7`. Threshold policy for TPR/FPR/PJA: **default** (calibrated on held-out clean benign prompts unless `default`).

## Within-condition AUROC (attack vs. benign twin)

| Guard | clean | zero_width | soft_hyphen | leetspeak | homoglyph | base64_wrap | base64_scaffold | rot13_wrap | rot13_scaffold | fullwidth | diacritics | spaced_letters |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| deepset | 0.886 | 0.458 | 0.554 | 0.437 | 0.728 | 0.373 | 0.811 | 0.326 | 0.769 | 0.886 | 0.501 | 0.458 |
| fmops | 0.914 | 0.914 | 0.914 | 0.457 | 0.539 | 0.510 | 0.585 | 0.328 | 0.668 | 0.492 | 0.914 | 0.620 |
| guardshield | 0.984 | 0.704 | 0.697 | 0.508 | 0.724 | 0.453 | 0.993 | 0.643 | 0.994 | 0.984 | 0.688 | 0.704 |
| perplexity_gpt2 | 0.631 | 0.381 | 0.432 | 0.480 | 0.413 | 0.392 | 0.583 | 0.423 | 0.605 | 0.341 | 0.380 | 0.241 |
| protectai_v2 | 1.000 | 0.586 | 0.730 | 0.380 | 0.902 | 0.497 | 0.997 | 0.530 | 0.997 | 1.000 | 0.689 | 0.586 |
| qwen3guard_gen_0_6b | 0.939 | 0.891 | 0.837 | 0.719 | 0.847 | 0.554 | 0.931 | 0.384 | 0.883 | 0.874 | 0.461 | 0.819 |

## Paired joint accuracy (%) at default

| Guard | clean | zero_width | soft_hyphen | leetspeak | homoglyph | base64_wrap | base64_scaffold | rot13_wrap | rot13_scaffold | fullwidth | diacritics | spaced_letters |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| deepset | 56.7 | 0.0 | 0.0 | 0.0 | 19.3 | 0.0 | 0.0 | 0.0 | 0.0 | 56.7 | 0.0 | 0.0 |
| fmops | 54.7 | 54.7 | 54.7 | 0.0 | 4.7 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 54.7 | 0.7 |
| guardshield | 90.7 | 4.7 | 0.7 | 4.7 | 10.7 | 2.0 | 90.0 | 21.3 | 89.3 | 90.7 | 1.3 | 4.7 |
| perplexity_gpt2 | — | — | — | — | — | — | — | — | — | — | — | — |
| protectai_v2 | 100.0 | 7.3 | 0.0 | 4.7 | 60.7 | 0.0 | 15.3 | 0.0 | 25.3 | 100.0 | 19.3 | 7.3 |
| qwen3guard_gen_0_6b | 52.0 | 60.7 | 59.3 | 4.0 | 50.7 | 0.0 | 63.3 | 0.0 | 13.3 | 55.3 | 10.7 | 47.3 |

## Attack recall / TPR (%) at default

| Guard | clean | zero_width | soft_hyphen | leetspeak | homoglyph | base64_wrap | base64_scaffold | rot13_wrap | rot13_scaffold | fullwidth | diacritics | spaced_letters |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| deepset | 92.7 | 100.0 | 100.0 | 99.3 | 96.0 | 100.0 | 100.0 | 100.0 | 100.0 | 92.7 | 100.0 | 100.0 |
| fmops | 93.3 | 93.3 | 93.3 | 98.7 | 92.0 | 100.0 | 100.0 | 100.0 | 100.0 | 22.7 | 93.3 | 100.0 |
| guardshield | 92.0 | 100.0 | 100.0 | 94.7 | 97.3 | 93.3 | 92.0 | 78.7 | 91.3 | 92.0 | 100.0 | 100.0 |
| perplexity_gpt2 | — | — | — | — | — | — | — | — | — | — | — | — |
| protectai_v2 | 100.0 | 98.7 | 100.0 | 60.0 | 92.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 94.0 | 98.7 |
| qwen3guard_gen_0_6b | 53.3 | 67.3 | 68.0 | 92.7 | 56.0 | 0.0 | 68.0 | 0.0 | 13.3 | 60.0 | 14.0 | 51.3 |

## Benign twin FPR (%) at default

| Guard | clean | zero_width | soft_hyphen | leetspeak | homoglyph | base64_wrap | base64_scaffold | rot13_wrap | rot13_scaffold | fullwidth | diacritics | spaced_letters |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| deepset | 36.7 | 100.0 | 100.0 | 100.0 | 78.0 | 100.0 | 100.0 | 100.0 | 100.0 | 36.7 | 100.0 | 100.0 |
| fmops | 38.7 | 38.7 | 38.7 | 99.3 | 89.3 | 100.0 | 100.0 | 100.0 | 100.0 | 33.3 | 38.7 | 99.3 |
| guardshield | 1.3 | 95.3 | 99.3 | 94.0 | 89.3 | 98.0 | 2.0 | 64.0 | 2.0 | 1.3 | 98.7 | 95.3 |
| perplexity_gpt2 | — | — | — | — | — | — | — | — | — | — | — | — |
| protectai_v2 | 0.0 | 92.0 | 100.0 | 74.0 | 34.0 | 100.0 | 84.7 | 100.0 | 74.7 | 0.0 | 78.7 | 92.0 |
| qwen3guard_gen_0_6b | 2.7 | 9.3 | 12.0 | 94.7 | 8.0 | 0.0 | 6.7 | 0.0 | 1.3 | 6.7 | 18.0 | 7.3 |

## FPR (%) after re-thresholding each condition to the clean TPR

| Guard | clean | zero_width | soft_hyphen | leetspeak | homoglyph | base64_wrap | base64_scaffold | rot13_wrap | rot13_scaffold | fullwidth | diacritics | spaced_letters |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| deepset | 35.3 | 92.0 | 91.3 | 94.7 | 66.7 | 94.7 | 32.0 | 98.0 | 45.3 | 35.3 | 94.7 | 92.0 |
| fmops | 36.7 | 36.7 | 36.7 | 97.3 | 90.0 | 99.3 | 81.3 | 97.3 | 64.7 | 79.3 | 36.7 | 80.7 |
| guardshield | 1.3 | 73.3 | 79.3 | 93.3 | 74.7 | 97.3 | 2.0 | 87.3 | 2.0 | 1.3 | 70.7 | 73.3 |
| perplexity_gpt2 | — | — | — | — | — | — | — | — | — | — | — | — |
| protectai_v2 | 0.0 | 93.3 | 90.7 | 100.0 | 92.0 | 98.7 | 0.7 | 99.3 | 0.7 | 0.0 | 94.7 | 93.3 |
| qwen3guard_gen_0_6b | 2.7 | 4.0 | 7.3 | 18.7 | 5.3 | 44.7 | 4.7 | 70.7 | 4.7 | 4.7 | 64.0 | 8.0 |
