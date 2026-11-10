# Audit 001 clarification — preserved negative evidence

The audit's executive-summary paragraph 3 says earlier intervals reproduce
closely except L37-L41. Its own complete table and JSON instead report 10 drift
intervals and 4 matches, including material L9-L11 drift. The table/JSON control
this count. The original audit remains unchanged; the inconsistency is preserved.

The task named L8-L9 actually spans [L7,L9] in its historical verifier. A chain
beginning from the inherited L7 frontier must cover [L7,L8] too. Starting at L8
alone would leave a gap and cannot promote a contiguous frontier to L9.

The stated [0.8,L7] frontier is inherited, not revalidated by Audit001. That audit
itself flags earlier verifiers for enclosure review. Revision38 records this
qualification explicitly. No new theorem or RH proof follows from the downgrade.
