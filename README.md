# pytoastapi

Python wrapper for Toast API

It's pretty simple:

```
toast = PyToast(client_id, secret) # you can optionally initialize the rguid parameter here

orders = toast.get_orders_by_day("20170908", rguid=rguid)

print(orders)

```
