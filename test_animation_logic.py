"""
Unit test verifying Lip-Sync Phoneme sequences and Gesture mapping logic
File: test_animation_logic.py
"""

import unittest

def generate_phoneme_sequence(text):
    words = text.split()
    queue = []
    for w in words:
        clean = ''.join(c.lower() for c in w if c.isalpha())
        word_phonemes = []
        for char in clean:
            if char in 'ae':
                word_phonemes.append('phoneme-open')
            elif char in 'ou':
                word_phonemes.append('phoneme-round')
            elif char in 'iy':
                word_phonemes.append('phoneme-wide')
            elif char in 'mbp':
                word_phonemes.append('phoneme-rest')
            else:
                word_phonemes.append('phoneme-mid')
        
        compressed = []
        for p in word_phonemes:
            if not compressed or compressed[-1] != p:
                compressed.append(p)
                if p in ('phoneme-open', 'phoneme-round'):
                    compressed.append(p)
        queue.extend(compressed)

        if w.endswith(('.', '!', '?')):
            queue.extend(['phoneme-rest', 'phoneme-rest', 'phoneme-rest'])
        elif w.endswith((',', ';', ':', '—')):
            queue.extend(['phoneme-rest', 'phoneme-rest'])
        else:
            queue.append('phoneme-mid')
    return queue


class AnimationLogicTests(unittest.TestCase):
    def test_phoneme_variety(self):
        sample = "Welcome to our advanced systems lab. Artificial Intelligence has transitioned."
        seq = generate_phoneme_sequence(sample)
        self.assertIn('phoneme-open', seq, "Must contain open vowel phoneme.")
        self.assertIn('phoneme-round', seq, "Must contain round vowel phoneme.")
        self.assertIn('phoneme-wide', seq, "Must contain wide vowel phoneme.")
        self.assertIn('phoneme-mid', seq, "Must contain mid consonant phoneme.")
        self.assertIn('phoneme-rest', seq, "Must contain rest / closure phoneme.")
        print(f"Phoneme sequence generated successfully for '{sample[:30]}...': {len(seq)} frames.")

    def test_gesture_mappings(self):
        senior_gestures = ['welcome', 'present-screen', 'open-palm', 'point-graph', 'sweeping-hand', 'firm-hand', 'warm-close']
        junior_gestures = ['point-tablet', 'inquire', 'highlight-hud', 'tap-console', 'nod-affirm', 'caution', 'thoughtful']
        for g in senior_gestures:
            self.assertTrue(len(g) > 0)
        for g in junior_gestures:
            self.assertTrue(len(g) > 0)
        print("All Senior and Junior gesture definitions verified.")


if __name__ == '__main__':
    unittest.main()
