import pandas as pd

class BillingAgent:
    def __init__(self, billing_data):
        self.billing_data = billing_data

    def generate_summary(self):
        total_billed = self.billing_data['Billed Amount'].sum()
        total_collected = self.billing_data['Collected Amount'].sum()
        total_outstanding = self.billing_data['Outstanding Amount'].sum()

        return {
            "Total Billed": total_billed,
            "Total Collected": total_collected,
            "Total Outstanding": total_outstanding,
        }

class TaxAgent:
    def __init__(self, tax_data):
        self.tax_data = tax_data

    def calculate_tax(self):
        self.tax_data['Total Tax'] = self.tax_data['CGST'] + self.tax_data['SGST'] + self.tax_data['IGST']
        return self.tax_data[['Invoice ID', 'Total Tax']]

class PartnerPerformanceAgent:
    def __init__(self, performance_data):
        self.performance_data = performance_data

    def generate_performance_summary(self):
        performance_summary = self.performance_data.groupby('Partner ID').agg({
            'Total Collections': 'sum',
            'Total Billed': 'sum'
        }).reset_index()
        performance_summary['Performance Score'] = performance_summary['Total Collections'] / performance_summary['Total Billed']
        return performance_summary

class ClientSummaryAgent:
    def __init__(self, client_data):
        self.client_data = client_data

    def generate_client_summaries(self):
        client_summary = self.client_data.groupby('Client ID').agg({
            'Transaction History': 'count',
            'Total Amount': 'sum'
        }).reset_index()
        return client_summary
