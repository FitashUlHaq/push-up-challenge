import React from "react";
import { TableBlock } from "../components/runtime/TableBlock";
import { MethodButton } from "../components/MethodButton";

const Record: React.FC = () => {
  return (
    <div id="page-record-1">
    <div id="izbgi" style={{"display": "flex", "height": "100vh", "fontFamily": "Arial, sans-serif", "--chart-color-palette": "default"}}>
      <nav id="imdic" style={{"width": "250px", "background": "linear-gradient(135deg, #4b3c82 0%, #5a3d91 100%)", "color": "white", "padding": "20px", "overflowY": "auto", "display": "flex", "flexDirection": "column", "--chart-color-palette": "default"}}>
        <h2 id="itqwo" style={{"marginTop": "0", "fontSize": "24px", "marginBottom": "30px", "fontWeight": "bold", "--chart-color-palette": "default"}}>{"BESSER"}</h2>
        <div id="idnf6" style={{"display": "flex", "flexDirection": "column", "flex": "1", "--chart-color-palette": "default"}}>
          <a id="iwaql" style={{"color": "white", "textDecoration": "none", "padding": "10px 15px", "display": "block", "background": "transparent", "borderRadius": "4px", "marginBottom": "5px", "--chart-color-palette": "default"}} href="/user">{"User"}</a>
          <a id="iow1b" style={{"color": "white", "textDecoration": "none", "padding": "10px 15px", "display": "block", "background": "rgba(255,255,255,0.2)", "borderRadius": "4px", "marginBottom": "5px", "--chart-color-palette": "default"}} href="/record">{"Record"}</a>
        </div>
        <p id="ir5qe" style={{"marginTop": "auto", "paddingTop": "20px", "borderTop": "1px solid rgba(255,255,255,0.2)", "fontSize": "11px", "opacity": "0.8", "textAlign": "center", "--chart-color-palette": "default"}}>{"© 2025 BESSER. All rights reserved."}</p>
      </nav>
      <main id="i1xog" style={{"flex": "1", "padding": "40px", "overflowY": "auto", "background": "#f5f5f5", "--chart-color-palette": "default"}}>
        <h1 id="i8okj" style={{"marginTop": "0", "color": "#333", "fontSize": "32px", "marginBottom": "10px", "--chart-color-palette": "default"}}>{"Record"}</h1>
        <p id="iujv1" style={{"color": "#666", "marginBottom": "30px", "--chart-color-palette": "default"}}>{"Manage Record data"}</p>
        <TableBlock id="table-record-1" styles={{"width": "100%", "minHeight": "400px", "--chart-color-palette": "default"}} title="Record List" options={{"showHeader": true, "stripedRows": false, "showPagination": true, "rowsPerPage": 5, "actionButtons": true, "columns": [{"label": "Date", "column_type": "field", "field": "date", "type": "date", "required": true}, {"label": "NumberOfPushups", "column_type": "field", "field": "numberOfPushups", "type": "int", "required": true}]}} dataBinding={{"entity": "Record", "endpoint": "/record/"}} />
        <div id="iwcxj" style={{"marginTop": "20px", "display": "flex", "gap": "10px", "flexWrap": "wrap", "--chart-color-palette": "default"}}>
          <MethodButton id="ihf65" className="action-button-component" style={{"display": "inline-flex", "alignItems": "center", "padding": "6px 14px", "background": "linear-gradient(90deg, #2563eb 0%, #1e40af 100%)", "color": "#fff", "textDecoration": "none", "borderRadius": "4px", "fontSize": "13px", "fontWeight": "600", "letterSpacing": "0.01em", "cursor": "pointer", "border": "none", "boxShadow": "0 1px 4px rgba(37,99,235,0.10)", "transition": "background 0.2s", "--chart-color-palette": "default"}} endpoint="/record/{record_id}/methods/update_record/" label="+ update_record" parameters={[{"name": "record", "type": "any", "required": true}]} isInstanceMethod={true} instanceSourceTableId="table-record-1" />
        </div>
      </main>
    </div>    </div>
  );
};

export default Record;
