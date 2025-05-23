from sqlmodelgen.codegen.code_ir.build_cir import gen_class_name

def test_gen_class_name():
    assert gen_class_name(table_name='hero', class_names={}) == 'Hero'
    assert gen_class_name(table_name='hero', class_names={'Hero'}) == 'HeroTable'
    assert gen_class_name(table_name='hero', class_names={'Hero', 'HeroTable'}) == 'HeroTableTable'