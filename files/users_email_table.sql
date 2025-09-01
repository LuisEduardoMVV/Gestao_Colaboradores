--
-- PostgreSQL database dump
--

-- Dumped from database version 16.8
-- Dumped by pg_dump version 17.5

-- Started on 2025-07-30 11:50:49

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 410 (class 1259 OID 26307)
-- Name: user_email; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_email (
    estabelecimento text,
    matricula text NOT NULL,
    nome text NOT NULL,
    data_admissao date NOT NULL,
    cargo_basico text,
    nivel_cargo text,
    cargo_basico_descricao text,
    unid_lotacao text,
    unid_lotacao_descricao text,
    unid_negocio text,
    unid_negocio_descricao text,
    centro_custo text,
    centro_custo_descricao text,
    supervisor text,
    coordenador text,
    gerente text,
    email text,
    created_by timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    modified_by timestamp with time zone,
    status text NOT NULL
);


ALTER TABLE public.user_email OWNER TO postgres;

--
-- TOC entry 5325 (class 0 OID 26307)
-- Dependencies: 410
-- Data for Name: user_email; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.user_email (estabelecimento, matricula, nome, data_admissao, cargo_basico, nivel_cargo, cargo_basico_descricao, unid_lotacao, unid_lotacao_descricao, unid_negocio, unid_negocio_descricao, centro_custo, centro_custo_descricao, supervisor, coordenador, gerente, email, created_by, modified_by, status) FROM stdin;
\.


--
-- TOC entry 5181 (class 2606 OID 26314)
-- Name: user_email user_email_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_email
    ADD CONSTRAINT user_email_pkey PRIMARY KEY (matricula);


-- Completed on 2025-07-30 11:50:49

--
-- PostgreSQL database dump complete
--

