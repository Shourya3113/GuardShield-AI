# Paired audit report: `obf_main`

Dataset `4ea17832e3273dc0`, commit `07d2abf0f617`. Threshold policy for TPR/FPR/PJA: **fpr@0.05** (calibrated on held-out clean benign prompts unless `default`).

## Within-condition AUROC (attack vs. benign twin)

| Guard | clean | zero_width | soft_hyphen | leetspeak | homoglyph | base64_wrap | base64_scaffold | rot13_wrap | rot13_scaffold | fullwidth | diacritics | spaced_letters |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| deepset | 0.871 | 0.522 | 0.566 | 0.407 | 0.683 | 0.330 | 0.795 | 0.353 | 0.728 | 0.871 | 0.525 | 0.522 |
| fmops | 0.900 | 0.900 | 0.900 | 0.471 | 0.528 | 0.500 | 0.548 | 0.351 | 0.638 | 0.487 | 0.900 | 0.623 |
| guardshield | 0.973 | 0.726 | 0.693 | 0.531 | 0.716 | 0.469 | 0.986 | 0.645 | 0.988 | 0.973 | 0.712 | 0.726 |
| horizon_guard_base | 1.000 | 1.000 | 1.000 | 0.908 | 0.996 | 0.549 | 0.999 | 0.687 | 0.983 | 1.000 | 0.954 | 0.951 |
| llama_guard_3_1b | 0.962 | 0.614 | 0.608 | 0.496 | 0.875 | 0.407 | 0.906 | 0.460 | 0.902 | 0.533 | 0.501 | 0.625 |
| llama_guard_3_8b | 0.968 | 0.915 | 0.893 | 0.426 | 0.933 | 0.453 | 0.957 | 0.476 | 0.961 | 0.595 | 0.677 | 0.890 |
| llama_guard_4_12b | 0.952 | 0.721 | 0.763 | 0.651 | 0.789 | 0.500 | 0.960 | 0.526 | 0.960 | 0.589 | 0.651 | 0.660 |
| mezzo_v2_base | 0.982 | 0.715 | 0.802 | 0.598 | 0.761 | 0.512 | 0.999 | 0.799 | 0.999 | 0.982 | 0.537 | 0.715 |
| perplexity_gpt2 | 0.700 | 0.378 | 0.432 | 0.500 | 0.428 | 0.403 | 0.638 | 0.480 | 0.661 | 0.352 | 0.371 | 0.242 |
| prompt_guard_2_22m | 0.999 | 0.999 | 0.526 | 0.319 | 0.502 | 0.535 | 0.999 | 0.335 | 0.999 | 0.999 | 0.467 | 0.999 |
| prompt_guard_2_86m | 1.000 | 1.000 | 0.515 | 0.483 | 0.929 | 0.596 | 1.000 | 0.384 | 1.000 | 1.000 | 0.527 | 1.000 |
| prompt_guard_v1 | 0.286 | 0.480 | 0.398 | 0.418 | 0.337 | 0.596 | 0.006 | 0.484 | 0.006 | 0.286 | 0.382 | 0.480 |
| prompt_guard_v1_jailbreak | 1.000 | 0.602 | 0.598 | 0.420 | 0.864 | 0.544 | 1.000 | 0.408 | 1.000 | 1.000 | 0.528 | 0.602 |
| protectai_v2 | 1.000 | 0.573 | 0.704 | 0.385 | 0.884 | 0.498 | 0.999 | 0.489 | 0.994 | 1.000 | 0.676 | 0.573 |
| qwen3guard_gen_0_6b | 0.936 | 0.862 | 0.804 | 0.646 | 0.816 | 0.589 | 0.931 | 0.348 | 0.880 | 0.828 | 0.436 | 0.795 |
| qwen3guard_gen_8b | 0.977 | 0.977 | 0.972 | 0.920 | 0.964 | 0.451 | 0.991 | 0.487 | 0.975 | 0.977 | 0.789 | 0.978 |
| sentinel_v2 | 1.000 | 0.953 | 0.927 | 0.703 | 0.986 | 0.502 | 0.999 | 0.538 | 0.998 | 0.876 | 0.772 | 0.949 |
| wildguard | 0.951 | 0.927 | 0.924 | 0.588 | 0.914 | 0.456 | 0.978 | 0.641 | 0.975 | 0.607 | 0.940 | 0.867 |

## Paired joint accuracy (%) at fpr@0.05

| Guard | clean | zero_width | soft_hyphen | leetspeak | homoglyph | base64_wrap | base64_scaffold | rot13_wrap | rot13_scaffold | fullwidth | diacritics | spaced_letters |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| deepset | 55.8 | 4.0 | 25.4 | 0.2 | 29.0 | 3.6 | 4.4 | 0.0 | 1.6 | 55.8 | 5.8 | 4.0 |
| fmops | 65.0 | 65.0 | 65.0 | 4.8 | 10.2 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 65.0 | 17.6 |
| guardshield | 88.2 | 0.6 | 0.0 | 0.0 | 1.2 | 0.0 | 61.0 | 0.0 | 71.2 | 88.2 | 0.0 | 0.6 |
| horizon_guard_base | 94.8 | 94.8 | 94.8 | 0.0 | 56.4 | 0.0 | 0.6 | 0.0 | 0.0 | 94.8 | 22.2 | 14.2 |
| llama_guard_3_1b | 81.0 | 27.0 | 29.4 | 2.8 | 59.8 | 0.0 | 50.2 | 0.8 | 55.8 | 1.4 | 20.4 | 32.8 |
| llama_guard_3_8b | 77.2 | 67.6 | 57.0 | 0.2 | 71.6 | 0.0 | 20.6 | 0.0 | 82.4 | 5.4 | 10.0 | 51.2 |
| llama_guard_4_12b | 79.8 | 22.4 | 24.0 | 0.0 | 16.4 | 0.0 | 0.8 | 0.0 | 1.0 | 0.0 | 9.6 | 12.0 |
| mezzo_v2_base | 87.8 | 0.2 | 0.0 | 0.0 | 0.0 | 0.0 | 42.8 | 0.0 | 28.0 | 87.8 | 0.0 | 0.2 |
| perplexity_gpt2 | 14.6 | 0.0 | 0.0 | 5.4 | 2.2 | 0.0 | 2.2 | 14.2 | 2.4 | 0.0 | 0.0 | 0.0 |
| prompt_guard_2_22m | 93.6 | 93.6 | 15.6 | 8.0 | 16.8 | 3.0 | 76.8 | 2.8 | 41.8 | 93.6 | 10.2 | 93.6 |
| prompt_guard_2_86m | 92.2 | 92.2 | 0.4 | 1.0 | 30.2 | 24.6 | 94.4 | 14.8 | 95.4 | 92.2 | 1.0 | 92.2 |
| prompt_guard_v1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| prompt_guard_v1_jailbreak | 88.2 | 0.6 | 1.4 | 0.0 | 15.0 | 3.0 | 84.4 | 14.8 | 79.0 | 88.2 | 0.4 | 0.6 |
| protectai_v2 | 94.4 | 0.2 | 0.0 | 0.0 | 2.2 | 0.0 | 0.0 | 0.0 | 2.2 | 94.4 | 0.0 | 0.2 |
| qwen3guard_gen_0_6b | 68.8 | 62.0 | 52.6 | 0.6 | 56.2 | 1.4 | 70.8 | 0.0 | 44.4 | 58.0 | 13.4 | 54.2 |
| qwen3guard_gen_8b | 85.4 | 82.0 | 76.6 | 14.4 | 76.4 | 0.0 | 15.6 | 0.0 | 77.6 | 82.6 | 9.4 | 78.2 |
| sentinel_v2 | 90.0 | 29.6 | 20.2 | 4.0 | 65.0 | 9.0 | 61.8 | 31.8 | 81.6 | 44.4 | 19.4 | 47.0 |
| wildguard | 76.4 | 73.6 | 71.2 | 4.4 | 66.6 | 10.2 | 90.2 | 0.2 | 78.8 | 13.0 | 71.2 | 61.4 |

## Attack recall / TPR (%) at fpr@0.05

| Guard | clean | zero_width | soft_hyphen | leetspeak | homoglyph | base64_wrap | base64_scaffold | rot13_wrap | rot13_scaffold | fullwidth | diacritics | spaced_letters |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| deepset | 69.0 | 99.8 | 33.0 | 99.4 | 76.8 | 85.4 | 100.0 | 100.0 | 100.0 | 69.0 | 96.6 | 99.8 |
| fmops | 71.8 | 71.8 | 71.8 | 70.0 | 61.6 | 100.0 | 100.0 | 100.0 | 100.0 | 0.0 | 71.8 | 81.4 |
| guardshield | 95.2 | 100.0 | 100.0 | 100.0 | 99.6 | 100.0 | 100.0 | 100.0 | 99.4 | 95.2 | 100.0 | 100.0 |
| horizon_guard_base | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 99.8 | 100.0 |
| llama_guard_3_1b | 87.6 | 75.4 | 86.0 | 98.8 | 85.2 | 100.0 | 99.0 | 99.6 | 97.8 | 99.6 | 78.2 | 70.0 |
| llama_guard_3_8b | 82.8 | 96.6 | 96.4 | 100.0 | 93.4 | 100.0 | 99.6 | 99.6 | 93.6 | 99.6 | 99.4 | 98.2 |
| llama_guard_4_12b | 85.2 | 93.6 | 95.0 | 100.0 | 97.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 96.8 | 92.4 |
| mezzo_v2_base | 96.2 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 96.2 | 100.0 | 100.0 |
| perplexity_gpt2 | 16.8 | 0.0 | 0.0 | 6.0 | 2.6 | 0.0 | 2.2 | 25.8 | 2.4 | 0.0 | 0.0 | 0.0 |
| prompt_guard_2_22m | 99.8 | 99.8 | 84.0 | 19.8 | 75.6 | 99.2 | 100.0 | 92.4 | 100.0 | 99.8 | 17.4 | 99.8 |
| prompt_guard_2_86m | 100.0 | 100.0 | 100.0 | 97.2 | 99.4 | 51.2 | 100.0 | 69.2 | 100.0 | 100.0 | 100.0 | 100.0 |
| prompt_guard_v1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| prompt_guard_v1_jailbreak | 100.0 | 99.8 | 100.0 | 100.0 | 100.0 | 3.4 | 100.0 | 56.8 | 100.0 | 100.0 | 100.0 | 99.8 |
| protectai_v2 | 100.0 | 100.0 | 100.0 | 99.4 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 |
| qwen3guard_gen_0_6b | 72.0 | 85.2 | 84.0 | 98.6 | 79.0 | 1.4 | 92.0 | 0.0 | 45.6 | 76.6 | 67.4 | 70.8 |
| qwen3guard_gen_8b | 92.0 | 96.4 | 95.8 | 99.8 | 95.2 | 100.0 | 100.0 | 100.0 | 98.6 | 95.6 | 97.4 | 97.8 |
| sentinel_v2 | 100.0 | 100.0 | 99.6 | 99.4 | 99.2 | 94.0 | 100.0 | 63.8 | 100.0 | 97.0 | 98.0 | 98.8 |
| wildguard | 82.2 | 85.2 | 82.4 | 99.2 | 73.6 | 32.4 | 98.4 | 0.2 | 83.0 | 13.8 | 77.4 | 84.2 |

## Benign twin FPR (%) at fpr@0.05

| Guard | clean | zero_width | soft_hyphen | leetspeak | homoglyph | base64_wrap | base64_scaffold | rot13_wrap | rot13_scaffold | fullwidth | diacritics | spaced_letters |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| deepset | 13.8 | 95.8 | 23.6 | 99.6 | 53.6 | 95.4 | 95.6 | 100.0 | 98.4 | 13.8 | 94.0 | 95.8 |
| fmops | 7.0 | 7.0 | 7.0 | 76.0 | 56.4 | 100.0 | 100.0 | 100.0 | 100.0 | 0.0 | 7.0 | 67.8 |
| guardshield | 7.0 | 99.4 | 100.0 | 100.0 | 98.6 | 100.0 | 39.0 | 100.0 | 28.4 | 7.0 | 100.0 | 99.4 |
| horizon_guard_base | 5.2 | 5.2 | 5.2 | 100.0 | 43.6 | 100.0 | 99.4 | 100.0 | 100.0 | 5.2 | 77.6 | 85.8 |
| llama_guard_3_1b | 7.0 | 61.6 | 62.6 | 97.2 | 27.6 | 100.0 | 49.2 | 99.2 | 42.4 | 98.6 | 71.0 | 52.2 |
| llama_guard_3_8b | 6.6 | 30.0 | 40.4 | 99.8 | 23.0 | 100.0 | 79.4 | 100.0 | 12.0 | 94.6 | 90.0 | 48.0 |
| llama_guard_4_12b | 7.4 | 76.2 | 74.4 | 100.0 | 83.0 | 100.0 | 99.2 | 100.0 | 99.0 | 100.0 | 90.0 | 85.0 |
| mezzo_v2_base | 8.6 | 99.8 | 100.0 | 100.0 | 100.0 | 100.0 | 57.2 | 100.0 | 72.0 | 8.6 | 100.0 | 99.8 |
| perplexity_gpt2 | 7.8 | 0.0 | 0.0 | 4.8 | 3.4 | 0.0 | 0.6 | 30.2 | 1.0 | 0.0 | 0.0 | 0.4 |
| prompt_guard_2_22m | 6.4 | 6.4 | 77.8 | 45.2 | 76.4 | 96.8 | 23.2 | 96.6 | 58.2 | 6.4 | 22.2 | 6.4 |
| prompt_guard_2_86m | 7.8 | 7.8 | 99.6 | 98.4 | 69.6 | 38.2 | 5.6 | 74.6 | 4.6 | 7.8 | 99.0 | 7.8 |
| prompt_guard_v1 | 8.2 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 51.4 | 0.2 | 60.8 | 8.2 | 0.0 | 0.0 |
| prompt_guard_v1_jailbreak | 11.8 | 99.4 | 98.6 | 100.0 | 85.0 | 2.2 | 15.6 | 69.0 | 21.0 | 11.8 | 99.6 | 99.4 |
| protectai_v2 | 5.6 | 99.8 | 100.0 | 100.0 | 97.8 | 100.0 | 100.0 | 100.0 | 97.8 | 5.6 | 100.0 | 99.8 |
| qwen3guard_gen_0_6b | 5.4 | 28.6 | 38.4 | 99.2 | 29.2 | 1.2 | 24.0 | 0.0 | 4.0 | 25.6 | 77.6 | 26.2 |
| qwen3guard_gen_8b | 7.4 | 15.6 | 20.2 | 85.6 | 19.8 | 100.0 | 84.4 | 100.0 | 21.2 | 13.8 | 90.4 | 20.4 |
| sentinel_v2 | 10.0 | 70.4 | 79.6 | 96.0 | 34.4 | 89.0 | 38.2 | 51.2 | 18.4 | 53.2 | 80.0 | 52.4 |
| wildguard | 7.4 | 13.6 | 13.0 | 95.6 | 9.0 | 41.2 | 8.6 | 0.2 | 5.4 | 8.8 | 8.2 | 27.2 |

## FPR (%) after re-thresholding each condition to the clean TPR

| Guard | clean | zero_width | soft_hyphen | leetspeak | homoglyph | base64_wrap | base64_scaffold | rot13_wrap | rot13_scaffold | fullwidth | diacritics | spaced_letters |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| deepset | 13.8 | 62.0 | 63.8 | 75.6 | 42.2 | 89.0 | 25.0 | 84.0 | 36.2 | 13.8 | 59.4 | 62.0 |
| fmops | 7.0 | 7.0 | 7.0 | 77.2 | 67.0 | 75.4 | 56.2 | 91.8 | 42.0 | 66.0 | 7.0 | 56.4 |
| guardshield | 6.0 | 80.6 | 86.0 | 95.8 | 86.4 | 97.6 | 5.8 | 93.4 | 5.4 | 6.0 | 76.2 | 80.6 |
| horizon_guard_base | 1.0 | 1.0 | 1.0 | 80.8 | 25.0 | 99.4 | 9.4 | 95.0 | 41.6 | 1.0 | 87.0 | 81.0 |
| llama_guard_3_1b | 7.0 | 72.4 | 63.6 | 87.6 | 34.2 | 94.6 | 14.0 | 84.2 | 18.4 | 88.2 | 79.4 | 73.8 |
| llama_guard_3_8b | 6.6 | 15.2 | 18.4 | 84.0 | 12.8 | 94.2 | 5.8 | 84.4 | 5.8 | 63.4 | 51.8 | 18.0 |
| llama_guard_4_12b | 7.4 | 59.4 | 48.8 | 68.0 | 47.8 | 87.0 | 6.0 | 87.2 | 4.8 | 72.4 | 68.6 | 67.8 |
| mezzo_v2_base | 8.0 | 81.8 | 64.8 | 91.4 | 66.0 | 97.8 | 0.6 | 71.8 | 0.6 | 8.0 | 96.0 | 81.8 |
| perplexity_gpt2 | 7.2 | 38.6 | 29.6 | 16.6 | 25.6 | 27.8 | 8.8 | 20.0 | 8.0 | 31.6 | 38.8 | 45.2 |
| prompt_guard_2_22m | 0.6 | 0.6 | 98.2 | 100.0 | 99.8 | 98.4 | 6.6 | 99.6 | 5.2 | 0.6 | 97.0 | 0.6 |
| prompt_guard_2_86m | 0.2 | 0.2 | 98.2 | 100.0 | 79.0 | 99.6 | 3.6 | 100.0 | 1.0 | 0.2 | 98.6 | 0.2 |
| prompt_guard_v1 | — | — | — | — | — | — | — | — | — | — | — | — |
| prompt_guard_v1_jailbreak | 0.0 | 99.6 | 94.8 | 100.0 | 78.6 | 100.0 | 2.0 | 100.0 | 1.0 | 0.0 | 98.0 | 99.6 |
| protectai_v2 | 0.0 | 96.6 | 90.0 | 100.0 | 91.8 | 99.0 | 1.0 | 100.0 | 1.8 | 0.0 | 95.4 | 96.6 |
| qwen3guard_gen_0_6b | 5.4 | 16.6 | 23.6 | 54.0 | 22.4 | 58.2 | 6.2 | 86.8 | 12.6 | 21.0 | 80.6 | 27.4 |
| qwen3guard_gen_8b | 7.2 | 8.4 | 9.2 | 33.6 | 10.2 | 95.6 | 3.6 | 86.8 | 12.2 | 8.6 | 68.6 | 8.8 |
| sentinel_v2 | 1.6 | 65.0 | 87.2 | 99.6 | 54.0 | 99.6 | 6.0 | 100.0 | 9.6 | 87.2 | 96.6 | 74.4 |
| wildguard | 6.8 | 10.6 | 13.0 | 70.2 | 15.0 | 80.8 | 3.8 | 62.4 | 5.0 | 58.8 | 11.2 | 23.0 |

## FPR (%) at the threshold catching 90% of the condition's attacks (threshold-free)

| Guard | clean | zero_width | soft_hyphen | leetspeak | homoglyph | base64_wrap | base64_scaffold | rot13_wrap | rot13_scaffold | fullwidth | diacritics | spaced_letters |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| deepset | 31.2 | 85.4 | 83.2 | 93.0 | 68.6 | 97.0 | 36.6 | 94.8 | 48.8 | 31.2 | 84.2 | 85.4 |
| fmops | 31.2 | 31.2 | 31.2 | 94.8 | 89.0 | 86.0 | 83.8 | 97.6 | 64.2 | 74.6 | 31.2 | 76.2 |
| guardshield | 1.8 | 66.8 | 78.2 | 91.4 | 74.8 | 94.8 | 2.4 | 87.0 | 2.2 | 1.8 | 66.0 | 66.8 |
| horizon_guard_base | 0.0 | 0.0 | 0.0 | 27.8 | 1.0 | 89.6 | 0.0 | 64.6 | 3.6 | 0.0 | 10.2 | 12.0 |
| llama_guard_3_1b | 8.8 | 74.4 | 65.8 | 90.2 | 37.4 | 94.6 | 18.0 | 87.0 | 21.4 | 90.2 | 80.6 | 76.6 |
| llama_guard_3_8b | 9.8 | 19.4 | 23.4 | 88.2 | 17.0 | 97.6 | 8.4 | 90.0 | 8.8 | 71.0 | 59.8 | 25.0 |
| llama_guard_4_12b | 11.2 | 71.4 | 60.8 | 79.6 | 62.0 | 92.6 | 8.8 | 92.0 | 9.4 | 81.4 | 74.0 | 79.6 |
| mezzo_v2_base | 0.4 | 69.6 | 46.8 | 81.0 | 53.8 | 90.4 | 0.2 | 54.2 | 0.2 | 0.4 | 91.0 | 69.6 |
| perplexity_gpt2 | 65.6 | 89.0 | 90.8 | 91.6 | 92.8 | 94.0 | 76.6 | 92.6 | 74.8 | 95.2 | 90.2 | 98.8 |
| prompt_guard_2_22m | 0.0 | 0.0 | 84.0 | 97.2 | 89.2 | 83.4 | 0.0 | 96.0 | 0.0 | 0.0 | 86.0 | 0.0 |
| prompt_guard_2_86m | 0.0 | 0.0 | 86.4 | 90.6 | 19.4 | 81.4 | 0.0 | 91.2 | 0.0 | 0.0 | 86.0 | 0.0 |
| prompt_guard_v1 | 83.8 | 79.4 | 93.2 | 96.0 | 85.2 | 82.8 | 100.0 | 89.0 | 100.0 | 83.8 | 87.0 | 79.4 |
| prompt_guard_v1_jailbreak | 0.0 | 74.8 | 83.8 | 96.0 | 40.0 | 92.2 | 0.0 | 95.4 | 0.0 | 0.0 | 81.2 | 74.8 |
| protectai_v2 | 0.0 | 74.4 | 62.0 | 95.2 | 34.8 | 86.2 | 0.2 | 91.0 | 1.2 | 0.0 | 71.8 | 74.4 |
| qwen3guard_gen_0_6b | 16.8 | 34.8 | 52.0 | 92.2 | 53.0 | 82.2 | 19.8 | 97.6 | 34.6 | 48.8 | 94.2 | 57.8 |
| qwen3guard_gen_8b | 4.8 | 6.4 | 7.2 | 24.8 | 8.2 | 93.8 | 3.4 | 84.8 | 8.8 | 6.2 | 62.2 | 5.6 |
| sentinel_v2 | 0.0 | 17.4 | 21.4 | 75.8 | 3.4 | 86.8 | 0.0 | 93.8 | 0.2 | 38.6 | 62.8 | 16.8 |
| wildguard | 14.0 | 22.8 | 23.8 | 78.0 | 24.2 | 85.4 | 5.4 | 72.0 | 6.2 | 72.8 | 18.6 | 37.2 |

## Intent signal (pre-registered; SPEC section 5)

| Guard | clean | zero_width | soft_hyphen | leetspeak | homoglyph | base64_wrap | base64_scaffold | rot13_wrap | rot13_scaffold | fullwidth | diacritics | spaced_letters |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| deepset | intact | **destroyed** | **destroyed** | **destroyed** | **destroyed** | **destroyed** | degraded | **destroyed** | degraded | intact | **destroyed** | **destroyed** |
| fmops | intact | intact | intact | **destroyed** | **destroyed** | **destroyed** | **destroyed** | **destroyed** | **destroyed** | **destroyed** | intact | **destroyed** |
| guardshield | intact | **destroyed** | **destroyed** | **destroyed** | **destroyed** | **destroyed** | intact | **destroyed** | intact | intact | **destroyed** | degraded |
| horizon_guard_base | intact | intact | intact | degraded | intact | **destroyed** | intact | **destroyed** | intact | intact | degraded | degraded |
| llama_guard_3_1b | intact | **destroyed** | **destroyed** | **destroyed** | degraded | **destroyed** | degraded | **destroyed** | degraded | **destroyed** | **destroyed** | **destroyed** |
| llama_guard_3_8b | intact | degraded | degraded | **destroyed** | degraded | **destroyed** | intact | **destroyed** | intact | **destroyed** | **destroyed** | degraded |
| llama_guard_4_12b | intact | degraded | degraded | **destroyed** | degraded | **destroyed** | intact | **destroyed** | intact | **destroyed** | **destroyed** | **destroyed** |
| mezzo_v2_base | intact | **destroyed** | degraded | **destroyed** | degraded | **destroyed** | intact | degraded | intact | intact | **destroyed** | **destroyed** |
| perplexity_gpt2 | **destroyed** | **destroyed** | **destroyed** | **destroyed** | **destroyed** | **destroyed** | **destroyed** | **destroyed** | **destroyed** | **destroyed** | **destroyed** | **destroyed** |
| prompt_guard_2_22m | intact | intact | **destroyed** | **destroyed** | **destroyed** | **destroyed** | intact | **destroyed** | intact | intact | **destroyed** | intact |
| prompt_guard_2_86m | intact | intact | **destroyed** | **destroyed** | degraded | **destroyed** | intact | **destroyed** | intact | intact | **destroyed** | intact |
| prompt_guard_v1 | **destroyed** | **destroyed** | **destroyed** | **destroyed** | **destroyed** | **destroyed** | **destroyed** | **destroyed** | **destroyed** | **destroyed** | **destroyed** | **destroyed** |
| prompt_guard_v1_jailbreak | intact | **destroyed** | **destroyed** | **destroyed** | degraded | **destroyed** | intact | **destroyed** | intact | intact | **destroyed** | **destroyed** |
| protectai_v2 | intact | **destroyed** | **destroyed** | **destroyed** | degraded | **destroyed** | intact | **destroyed** | intact | intact | **destroyed** | **destroyed** |
| qwen3guard_gen_0_6b | intact | degraded | degraded | **destroyed** | degraded | **destroyed** | intact | **destroyed** | degraded | degraded | **destroyed** | degraded |
| qwen3guard_gen_8b | intact | intact | intact | degraded | intact | **destroyed** | intact | **destroyed** | intact | intact | degraded | intact |
| sentinel_v2 | intact | degraded | degraded | **destroyed** | intact | **destroyed** | intact | **destroyed** | intact | degraded | degraded | degraded |
| wildguard | intact | intact | intact | **destroyed** | degraded | **destroyed** | intact | **destroyed** | intact | **destroyed** | intact | degraded |

## Failure mode at fpr@0.05 (pre-registered; SPEC section 5)

| Guard | clean | zero_width | soft_hyphen | leetspeak | homoglyph | base64_wrap | base64_scaffold | rot13_wrap | rot13_scaffold | fullwidth | diacritics | spaced_letters |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| deepset | · | **closed** | **open** | **closed** | **closed** | **closed** | **closed** | **closed** | **closed** | · | **closed** | **closed** |
| fmops | · | · | · | **closed** | **closed** | **closed** | **closed** | **closed** | **closed** | **open** | · | **closed** |
| guardshield | · | **closed** | **closed** | **closed** | **closed** | **closed** | **closed** | **closed** | **closed** | · | **closed** | **closed** |
| horizon_guard_base | · | · | · | **closed** | **closed** | **closed** | **closed** | **closed** | **closed** | · | **closed** | **closed** |
| llama_guard_3_1b | · | **closed** | **closed** | **closed** | **closed** | **closed** | **closed** | **closed** | **closed** | **closed** | **closed** | **closed** |
| llama_guard_3_8b | · | **closed** | **closed** | **closed** | · | **closed** | **closed** | **closed** | · | **closed** | **closed** | **closed** |
| llama_guard_4_12b | · | **closed** | **closed** | **closed** | **closed** | **closed** | **closed** | **closed** | **closed** | **closed** | **closed** | **closed** |
| mezzo_v2_base | · | **closed** | **closed** | **closed** | **closed** | **closed** | **closed** | **closed** | **closed** | · | **closed** | **closed** |
| perplexity_gpt2 | · | · | · | · | · | · | · | **closed** | · | · | · | · |
| prompt_guard_2_22m | · | · | **closed** | **both** | **both** | **closed** | · | **closed** | **closed** | · | **open** | · |
| prompt_guard_2_86m | · | · | **closed** | **closed** | **closed** | **both** | · | **both** | · | · | **closed** | · |
| prompt_guard_v1 | · | · | · | · | · | · | **closed** | · | **closed** | · | · | · |
| prompt_guard_v1_jailbreak | · | **closed** | **closed** | **closed** | **closed** | **open** | · | **both** | · | · | **closed** | **closed** |
| protectai_v2 | · | **closed** | **closed** | **closed** | **closed** | **closed** | **closed** | **closed** | **closed** | · | **closed** | **closed** |
| qwen3guard_gen_0_6b | · | **closed** | **closed** | **closed** | **closed** | **open** | · | **open** | **open** | **closed** | **closed** | **closed** |
| qwen3guard_gen_8b | · | · | · | **closed** | · | **closed** | **closed** | **closed** | · | · | **closed** | · |
| sentinel_v2 | · | **closed** | **closed** | **closed** | **closed** | **closed** | **closed** | **both** | · | **closed** | **closed** | **closed** |
| wildguard | · | · | · | **closed** | · | **both** | · | **open** | · | **open** | · | · |

## Length confound (AUROC of character length, attack vs twin; 0.5 = none)

| clean | zero_width | soft_hyphen | leetspeak | homoglyph | base64_wrap | base64_scaffold | rot13_wrap | rot13_scaffold | fullwidth | diacritics | spaced_letters |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0.500 | 0.516 | 0.516 | 0.500 | 0.500 | 0.500 | 0.500 | 0.500 | 0.500 | 0.500 | 0.514 | 0.516 |
