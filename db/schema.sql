-- Snapshot généré par fastapi-forge à partir de la base introspectée.
-- Structure uniquement (pas de données). Régénéré par `forge sync`.
CREATE TYPE order_status AS ENUM ('pending', 'paid', 'shipped', 'cancelled');

CREATE TABLE public.categories (
	code VARCHAR(20) NOT NULL, 
	label VARCHAR(100) NOT NULL, 
	CONSTRAINT categories_pkey PRIMARY KEY (code)
);

CREATE TABLE public.customers (
	id BIGINT GENERATED ALWAYS AS IDENTITY (INCREMENT BY 1 START WITH 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1 NO CYCLE), 
	email VARCHAR(255) NOT NULL, 
	full_name VARCHAR(120) NOT NULL, 
	is_active BOOLEAN DEFAULT true NOT NULL, 
	metadata JSONB, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	CONSTRAINT customers_pkey PRIMARY KEY (id), 
	CONSTRAINT customers_email_key UNIQUE NULLS DISTINCT (email)
);

CREATE TABLE public.orders (
	id SERIAL NOT NULL, 
	customer_id BIGINT NOT NULL, 
	status order_status DEFAULT 'pending'::order_status NOT NULL, 
	ordered_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	note TEXT, 
	CONSTRAINT orders_pkey PRIMARY KEY (id), 
	CONSTRAINT orders_customer_id_fkey FOREIGN KEY(customer_id) REFERENCES public.customers (id)
);

CREATE TABLE public.products (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	sku VARCHAR(40) NOT NULL, 
	name VARCHAR(200) NOT NULL, 
	price NUMERIC(10, 2) NOT NULL, 
	category_code VARCHAR(20), 
	stock INTEGER DEFAULT 0 NOT NULL, 
	CONSTRAINT products_pkey PRIMARY KEY (id), 
	CONSTRAINT products_category_code_fkey FOREIGN KEY(category_code) REFERENCES public.categories (code), 
	CONSTRAINT products_sku_key UNIQUE NULLS DISTINCT (sku), 
	CONSTRAINT products_price_check CHECK (price >= 0::numeric)
);
