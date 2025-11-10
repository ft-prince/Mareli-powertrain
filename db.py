import psycopg2
from psycopg2 import sql
import json

# Database connection parameters
DB_CONFIG = {
    'dbname': 'demo',
    'user': 'postgres',
    'password': 'newpassword18',
    'host': 'localhost',
    'port': '5433'
}

def fetch_all_table_structures():
    """Fetch complete structure of all tables in the database"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # Get all table names from public schema
        cur.execute("""
            SELECT tablename 
            FROM pg_tables 
            WHERE schemaname = 'public'
            ORDER BY tablename;
        """)
        
        tables = cur.fetchall()
        all_table_info = {}
        
        print("=" * 100)
        print("POSTGRESQL DATABASE STRUCTURE - COMPLETE ANALYSIS")
        print("=" * 100)
        print(f"Total Tables Found: {len(tables)}\n")
        
        for (table_name,) in tables:
            print(f"\n{'='*100}")
            print(f"TABLE: {table_name}")
            print(f"{'='*100}")
            
            # Get column information with detailed metadata
            cur.execute("""
                SELECT 
                    c.column_name,
                    c.data_type,
                    c.character_maximum_length,
                    c.numeric_precision,
                    c.numeric_scale,
                    c.is_nullable,
                    c.column_default,
                    c.udt_name
                FROM information_schema.columns c
                WHERE c.table_schema = 'public' 
                AND c.table_name = %s
                ORDER BY c.ordinal_position;
            """, (table_name,))
            
            columns = cur.fetchall()
            
            # Get primary keys
            cur.execute("""
                SELECT a.attname
                FROM pg_index i
                JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
                WHERE i.indrelid = %s::regclass AND i.indisprimary;
            """, (table_name,))
            
            primary_keys = [row[0] for row in cur.fetchall()]
            
            # Get foreign keys
            cur.execute("""
                SELECT
                    kcu.column_name,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name
                FROM information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name
                    AND tc.table_schema = kcu.table_schema
                JOIN information_schema.constraint_column_usage AS ccu
                    ON ccu.constraint_name = tc.constraint_name
                    AND ccu.table_schema = tc.table_schema
                WHERE tc.constraint_type = 'FOREIGN KEY' 
                AND tc.table_name = %s;
            """, (table_name,))
            
            foreign_keys = cur.fetchall()
            
            # Get indexes
            cur.execute("""
                SELECT
                    i.relname as index_name,
                    a.attname as column_name,
                    ix.indisunique as is_unique
                FROM pg_class t
                JOIN pg_index ix ON t.oid = ix.indrelid
                JOIN pg_class i ON i.oid = ix.indexrelid
                JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = ANY(ix.indkey)
                WHERE t.relname = %s
                AND t.relkind = 'r'
                ORDER BY i.relname;
            """, (table_name,))
            
            indexes = cur.fetchall()
            
            # Store table structure
            table_info = {
                'columns': [],
                'primary_keys': primary_keys,
                'foreign_keys': [],
                'indexes': []
            }
            
            # Print column details
            print(f"\n{'Column Name':<25} {'Data Type':<20} {'Length':<10} {'Nullable':<10} {'Default':<30}")
            print("-" * 100)
            
            for col in columns:
                col_name, data_type, max_length, num_precision, num_scale, nullable, default, udt_name = col
                
                # Format type string
                if max_length:
                    type_str = f"{data_type}({max_length})"
                elif num_precision:
                    type_str = f"{data_type}({num_precision},{num_scale})" if num_scale else f"{data_type}({num_precision})"
                else:
                    type_str = data_type
                
                # Check if primary key
                pk_marker = " [PK]" if col_name in primary_keys else ""
                
                col_info = {
                    'name': col_name,
                    'data_type': data_type,
                    'max_length': max_length,
                    'numeric_precision': num_precision,
                    'numeric_scale': num_scale,
                    'nullable': nullable == 'YES',
                    'default': default,
                    'udt_name': udt_name,
                    'is_primary_key': col_name in primary_keys
                }
                
                table_info['columns'].append(col_info)
                
                # Print formatted
                nullable_str = 'NULL' if nullable == 'YES' else 'NOT NULL'
                default_str = str(default)[:28] if default else ''
                
                print(f"{col_name + pk_marker:<25} {type_str:<20} {str(max_length or ''):<10} {nullable_str:<10} {default_str:<30}")
            
            # Print foreign keys
            if foreign_keys:
                print(f"\n{'Foreign Keys:':<25}")
                print("-" * 100)
                for fk in foreign_keys:
                    col_name, ref_table, ref_col = fk
                    print(f"  {col_name} -> {ref_table}({ref_col})")
                    table_info['foreign_keys'].append({
                        'column': col_name,
                        'references_table': ref_table,
                        'references_column': ref_col
                    })
            
            # Print indexes
            if indexes:
                print(f"\n{'Indexes:':<25}")
                print("-" * 100)
                seen_indexes = set()
                for idx in indexes:
                    idx_name, col_name, is_unique = idx
                    if idx_name not in seen_indexes:
                        unique_str = " (UNIQUE)" if is_unique else ""
                        print(f"  {idx_name}{unique_str}")
                        seen_indexes.add(idx_name)
                        table_info['indexes'].append({
                            'name': idx_name,
                            'is_unique': is_unique
                        })
            
            all_table_info[table_name] = table_info
        
        cur.close()
        conn.close()
        
        # Save to JSON file
        output_file = 'database_complete_structure.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_table_info, f, indent=2, default=str)
        
        print("\n" + "=" * 100)
        print(f"✅ SUCCESS: Fetched complete structure of {len(all_table_info)} tables")
        print(f"📁 Saved to: {output_file}")
        print("=" * 100)
        
        # Print summary
        print("\n" + "=" * 100)
        print("TABLE SUMMARY")
        print("=" * 100)
        for table_name, info in all_table_info.items():
            print(f"{table_name:<35} - {len(info['columns'])} columns, {len(info['primary_keys'])} PK, {len(info['foreign_keys'])} FK")
        
        return all_table_info
        
    except psycopg2.Error as e:
        print(f"❌ Database Error: {e}")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def get_table_sample_data(table_name, limit=5):
    """Fetch sample data from a specific table"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        print(f"\n{'='*100}")
        print(f"SAMPLE DATA FROM: {table_name} (First {limit} rows)")
        print(f"{'='*100}\n")
        
        # Get column names
        cur.execute(sql.SQL("SELECT * FROM {} LIMIT 0").format(sql.Identifier(table_name)))
        column_names = [desc[0] for desc in cur.description]
        
        # Get sample data
        cur.execute(sql.SQL("SELECT * FROM {} LIMIT %s").format(sql.Identifier(table_name)), (limit,))
        rows = cur.fetchall()
        
        if rows:
            # Print header
            header = " | ".join(f"{col:<20}" for col in column_names)
            print(header)
            print("-" * len(header))
            
            # Print rows
            for row in rows:
                print(" | ".join(f"{str(val):<20}" for val in row))
        else:
            print("No data found in this table.")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error fetching sample data: {e}")


if __name__ == "__main__":
    print("\n🔍 Starting PostgreSQL Database Structure Analysis...\n")
    
    # Fetch all table structures
    structures = fetch_all_table_structures()
    
    if structures:
        print("\n\n📊 Would you like to see sample data from any table?")
        print("You can call: get_table_sample_data('table_name', limit=5)")
        
        # Example: Uncomment to see sample data
        # get_table_sample_data('cnc1_postprocessing', limit=3)
        # get_table_sample_data('cnc1_preprocessing', limit=3)