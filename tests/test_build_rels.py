'''
testing functions used to build relationships amongst models
'''


from sqlmodelgen.codegen.code_ir.build_rels import (
    gen_m2o_candidate_names,
    gen_o2m_candidate_names,
)


def test_gen_m2o_candidate_names():
    gen = gen_m2o_candidate_names('athletes')

    assert next(gen) == 'athletess'
    assert next(gen) == 'athletess0'
    assert next(gen) == 'athletess1'

def test_gen_o2m_candidate_names():

    gen = gen_o2m_candidate_names('key_id')

    assert next(gen) == 'key'
    assert next(gen) == 'key_rel'
    assert next(gen) == 'key_rel0'
    assert next(gen) == 'key_rel1'

    gen = gen_o2m_candidate_names('keyid')

    assert next(gen) == 'key'
    assert next(gen) == 'key_rel'
    assert next(gen) == 'key_rel0'
    assert next(gen) == 'key_rel1'

    gen = gen_o2m_candidate_names('key')

    assert next(gen) == 'key_rel'
    assert next(gen) == 'key_rel0'
    assert next(gen) == 'key_rel1'
