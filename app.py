import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, dash_table, callback
import dash_bootstrap_components as dbc

# Initialize the app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Load data
# Assuming you have a CSV file with the data
df = pd.read_csv('transactions.csv')

# Data preprocessing
df['Transaction_Date'] = pd.to_datetime(df['Transaction_Date'])
df['Location'] = df['Location'].apply(lambda x: str(x).title()).astype('category')
df['Date'] = pd.to_datetime(df['Date'])
df['Total_Spend'] = df['Offline_Spend'] + df['Online_Spend']
df['Revenue'] = df['Quantity'] * df['Avg_Price']

# Calculate metrics
total_revenue = df['Revenue'].sum()
avg_order_value = df.groupby('Transaction_ID')['Revenue'].sum().mean()
total_customers = df['CustomerID'].nunique()
top_categories = df.groupby('Product_Category')['Revenue'].sum().sort_values(ascending=False).head(5)

# App layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Customer Transaction Dashboard", className="text-center my-2"), width=12)
    ]),
    
    # KPI Cards
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H4("Total Revenue", className="card-title"),
                html.H2(f"${total_revenue:,.2f}", className="card-text")
            ])
        ], color="primary", outline=True), width=3),
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H4("Avg Order Value", className="card-title"),
                html.H2(f"${avg_order_value:,.2f}", className="card-text")
            ])
        ], color="success", outline=True), width=3),
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H4("Total Customers", className="card-title"),
                html.H2(f"{total_customers:,}", className="card-text")
            ])
        ], color="info", outline=True), width=3),
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H4("Online/Offline Ratio", className="card-title"),
                html.H2(f"{df['Online_Spend'].sum() / df['Offline_Spend'].sum():.2f}", className="card-text")
            ])
        ], color="warning", outline=True), width=3),
    ], className="mb-4"),
    
    # Filters
    dbc.Row([ 
        dbc.Col([
            html.Label("Product Category:", className="mt-3"),
            dcc.Dropdown(
                id='category-filter',
                options=[{'label': cat, 'value': cat} for cat in sorted(df['Product_Category'].dropna().unique())],
                multi=True
            ),
        ], width=6),
        dbc.Col([  
            html.Label("Location:", className="mt-3"),
            dcc.Dropdown(
                id='location-filter',
                options=[{'label': loc, 'value': loc} for loc in sorted(df['Location'].dropna().unique())],
                multi=True
            ),
        ], width=6),
    ], className="mb-4"),
    
    # Tabs for different visualizations
    dbc.Tabs([
        # Sales Trends Tab
        dbc.Tab(label="Sales Trends", children=[
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("Monthly Sales Trend"),
                            dcc.Graph(id='sales-trend')
                        ])
                    ])
                ], width=12)
            ], className="mt-4"),
        ]),
        
        # Product Analysis Tab
        dbc.Tab(label="Product Analysis", children=[
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("Revenue by Product Category"),
                            dcc.Graph(id='category-revenue')
                        ])
                    ])
                ], width=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("Top Products by Quantity Sold"),
                            dcc.Graph(id='top-products')
                        ])
                    ])
                ], width=6)
            ], className="mt-4")
        ]),
        
        # Customer Analysis Tab
        dbc.Tab(label="Customer Analysis", children=[
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("Customer Spending by Gender"),
                            dcc.Graph(id='gender-spending')
                        ])
                    ])
                ], width=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("Spending by Tenure"),
                            dcc.Graph(id='tenure-spending')
                        ])
                    ])
                ], width=6)
            ], className="mt-4"),
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("Regional Spending Distribution"),
                            dcc.Graph(id='location-spending')
                        ])
                    ])
                ], width=12)
            ], className="mt-4")
        ]),
        
        # Coupon Analysis
        dbc.Tab(label="Coupon Analysis", children=[
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("Coupon Effectiveness"),
                            dcc.Graph(id='coupon-effectiveness')
                        ])
                    ])
                ], width=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("Discount Impact on Order Value"),
                            dcc.Graph(id='discount-impact')
                        ])
                    ])
                ], width=6)
            ], className="mt-4")
        ]),
        
        # Transaction Details Tab
        dbc.Tab(label="Transaction Details", children=[
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("Transaction Data"),
                            dash_table.DataTable(
                                id='transaction-table',
                                columns=[{"name": i, "id": i} for i in df.columns],
                                data=df.head(100).to_dict('records'),
                                page_size=15,
                                style_table={'overflowX': 'auto'},
                                style_cell={
                                    'minWidth': '100px',
                                    'textAlign': 'left'
                                },
                                filter_action="native",
                                sort_action="native"
                            )
                        ])
                    ])
                ], width=12)
            ], className="mt-4")
        ])
    ])
], fluid=True)

# Callbacks for interactive elements
@callback(
    [Output('sales-trend', 'figure'),
     Output('category-revenue', 'figure'),
     Output('top-products', 'figure'),
     Output('gender-spending', 'figure'),
     Output('tenure-spending', 'figure'),
     Output('location-spending', 'figure'),
     Output('coupon-effectiveness', 'figure'),
     Output('discount-impact', 'figure'),
     Output('transaction-table', 'data')],
    [Input('category-filter', 'value'),
     Input('location-filter', 'value')]
)
def update_graphs(categories, locations):
    # Filter data based on inputs
    filtered_df = df.copy()

    if categories:
        filtered_df = filtered_df[filtered_df['Product_Category'].isin(categories)]
    
    if locations:
        filtered_df = filtered_df[filtered_df['Location'].isin(locations)]
    
    # Monthly sales trend
    monthly_sales = filtered_df.groupby(pd.Grouper(key='Transaction_Date', freq='M'))['Revenue'].sum().reset_index()
    sales_trend_fig = px.line(monthly_sales, x='Transaction_Date', y='Revenue',
                         title='Monthly Sales Trend',
                         labels={'Revenue': 'Revenue ($)', 'Transaction_Date': 'Date'})
    
    # Category revenue
    category_revenue = filtered_df.groupby('Product_Category')['Revenue'].sum().reset_index().sort_values('Revenue', ascending=False)
    category_fig = px.bar(category_revenue, x='Product_Category', y='Revenue',
                         title='Revenue by Product Category',
                         labels={'Revenue': 'Revenue ($)', 'Product_Category': 'Category'})
    
    # Top products
    top_products = filtered_df.groupby('Product_Description')['Quantity'].sum().reset_index().sort_values('Quantity', ascending=False).head(10)
    products_fig = px.bar(top_products, x='Product_Description', y='Quantity',
                        title='Top 10 Products by Quantity Sold',
                        labels={'Quantity': 'Units Sold', 'Product_Description': 'Product'})
    products_fig.update_layout(xaxis={'categoryorder':'total descending'})
    
    # Gender spending
    gender_spending = filtered_df.groupby('Gender')[['Online_Spend', 'Offline_Spend']].sum().reset_index()
    gender_fig = px.bar(gender_spending, x='Gender', y=['Online_Spend', 'Offline_Spend'],
                      title='Spending by Gender',
                      labels={'value': 'Spend ($)', 'variable': 'Channel'})
    
    # Tenure spending
    tenure_bins = [0, 6, 12, 24, 36, float('inf')]
    tenure_labels = ['0-6', '7-12', '13-24', '25-36', '36+']
    filtered_df['Tenure_Group'] = pd.cut(filtered_df['Tenure_Months'], bins=tenure_bins, labels=tenure_labels)
    tenure_spending = filtered_df.groupby('Tenure_Group')['Total_Spend'].mean().reset_index()
    tenure_fig = px.bar(tenure_spending, x='Tenure_Group', y='Total_Spend',
                      title='Average Spending by Customer Tenure (Months)',
                      labels={'Total_Spend': 'Avg. Spend ($)', 'Tenure_Group': 'Tenure (Months)'})
    
    # Location spending
    location_spending = filtered_df.groupby('Location')['Total_Spend'].sum().reset_index().sort_values('Total_Spend', ascending=False)
    location_fig = px.bar(location_spending, x='Location', y='Total_Spend',
                         title='Total Spending by Location',
                         labels={'Total_Spend': 'Total Spend ($)', 'Location': 'Location'})
    
    # Coupon effectiveness
    coupon_effect = filtered_df.groupby('Coupon_Status')['Revenue'].mean().reset_index()
    coupon_fig = px.bar(coupon_effect, x='Coupon_Status', y='Revenue',
                       title='Average Order Value by Coupon Status',
                       labels={'Revenue': 'Avg. Order Value ($)', 'Coupon_Status': 'Coupon Status'})
    
    # Discount impact
    filtered_df['Discount_Group'] = pd.cut(filtered_df['Discount_pct'], 
                                          bins=[0, 5, 10, 15, 20, 100],
                                          labels=['0-5%', '5-10%', '10-15%', '15-20%', '20%+'])
    discount_impact = filtered_df.groupby('Discount_Group')['Revenue'].mean().reset_index()
    discount_fig = px.line(discount_impact, x='Discount_Group', y='Revenue',
                          title='Average Order Value by Discount Percentage',
                          labels={'Revenue': 'Avg. Order Value ($)', 'Discount_Group': 'Discount Range'})
    
    # Transaction table
    table_data = filtered_df.head(100).to_dict('records')
    
    return (sales_trend_fig, category_fig, products_fig, gender_fig, tenure_fig, 
            location_fig, coupon_fig, discount_fig, table_data)

if __name__ == '__main__':
    app.run_server(debug=True, port=8050)