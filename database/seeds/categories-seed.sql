-- CATEGORIAS
INSERT INTO categorias (id_categoria, nome) VALUES (1, 'Periféricos') ON CONFLICT (id_categoria) DO NOTHING;
INSERT INTO categorias (id_categoria, nome) VALUES (2, 'Hardware') ON CONFLICT (id_categoria) DO NOTHING;
INSERT INTO categorias (id_categoria, nome) VALUES (3, 'Monitores') ON CONFLICT (id_categoria) DO NOTHING;
INSERT INTO categorias (id_categoria, nome) VALUES (4, 'Acessórios de TI') ON CONFLICT (id_categoria) DO NOTHING;
INSERT INTO categorias (id_categoria, nome) VALUES (5, 'Móveis de Escritório') ON CONFLICT (id_categoria) DO NOTHING;
INSERT INTO categorias (id_categoria, nome) VALUES (6, 'Áudio') ON CONFLICT (id_categoria) DO NOTHING;
INSERT INTO categorias (id_categoria, nome) VALUES (7, 'Armazenamento') ON CONFLICT (id_categoria) DO NOTHING;
INSERT INTO categorias (id_categoria, nome) VALUES (8, 'Redes e Conectividade') ON CONFLICT (id_categoria) DO NOTHING;
