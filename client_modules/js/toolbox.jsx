// Remaining field types not yet implemented: 
// class RadioButton extends React.Component {}
// class Anchor extends React.Component {}
// class Checkbox extends React.Component {}

// TODO: Discuss with Ray how this might work with/conflict with the CSpace UI rewrite. 
var React = require('react');
var ReactDOM = require('react-dom');
var Autosuggest = require('react-autosuggest');
var $ = require("expose-loader?$!jquery");

// custom propType
function tuple(props, propName, componentName) {
  componentName = componentName || 'ANONYMOUS';
  if (props[propName]) {
    let value = props[propName];
    if (Array.isArray(value)) {
      return value.length == 2 ? null : new Error(propName + ' in ' + componentName + " is not a tuple.")
    }
  }
  return null;
}

// https://www.ian-thomas.net/custom-proptype-validation-with-react/
function createChainableTypeChecker(validate) {
  function checkType(isRequired, props, propName, componentName, location) {
    componentName = componentName || ANONYMOUS;
    if (props[propName] == null) {
      var locationName = ReactPropTypeLocationNames[location];
      if (isRequired) {
        return new Error(
          ("Required " + locationName + " `" + propName + "` was not specified in ") +
          ("`" + componentName + "`.")
        );
      }
      return null;
    } else {
      return validate(props, propName, componentName, location);
    }
  }

  let chainedCheckType = checkType.bind(null, false);
  chainedCheckType.isRequired = checkType.bind(null, true);

  return chainedCheckType;
}

class AutosuggestInput extends React.Component {
  constructor(props) {
    super(props);
    if ('defaultValue' in this.props && this.props.defaultValue !== null) {
      this.state = {value: this.props.defaultValue, suggestions: [], isLoading: false};
    } else {
      this.state = {value: '', suggestions: [], isLoading: false};
    }

    this.lastRequestId = null;
    this.handleChange = this.handleChange.bind(this);
    this.onSuggestionsFetchRequested = this.onSuggestionsFetchRequested.bind(this);
    this.onSuggestionsClearRequested = this.onSuggestionsClearRequested.bind(this);
  }

  loadSuggestions(value) {
    // Cancel the previous request
    if (this.lastRequestId !== null) {
      clearTimeout(this.lastRequestId);
    }

    this.setState({isLoading: true});

    var elementID = this.props.data.name;
    this.lastRequestId = setTimeout(() => {
      $.ajax({
        url: "../../suggest/?",
        dataType: "json",
        data: {
          q: value,
          elementID: elementID,
          source: 'postgres'
        },
        success: ((data) => {
          if ('s' in data[data.length - 1]) {
            data.pop();
          }
          this.setState({
            isLoading: false,
            suggestions: data
          });
        })
      });
    }, 1000);
  }

  handleChange(event, { newValue, method }) {
    this.setState({value: newValue});
  }

  onSuggestionsFetchRequested({ value }) {
    this.loadSuggestions(value);
  }

  onSuggestionsClearRequested() {
    this.setState({
      suggestions: []
    });
  };

  onSuggestionSelected(event, { suggestion, suggestionValue, suggestionIndex, sectionIndex, method }) {
    //prevents event from bubbling up to form submission
    event.preventDefault();
  }

  getSuggestionValue(suggestion) {
    return suggestion.value;
  }

  renderSuggestion(suggestion) {
    return (
      <span>{suggestion.value}</span>
    );
  }

  render() {
    const { value, suggestions, isLoading } = this.state;
    const inputProps = {
      placeholder: value,
      type: 'text',
      name: this.props.data.name,
      maxLength: this.props.data.parameter,
      value: value,
      onChange: this.handleChange
    };

    // const status = (isLoading ? 'Loading...' : 'Type to load suggestions');
    // <div className="status">
    //   <strong>Status:</strong> {status}
    // </div>

    return (
      <td>
        <Autosuggest
          suggestions={suggestions}
          onSuggestionsFetchRequested={this.onSuggestionsFetchRequested}
          onSuggestionsClearRequested={this.onSuggestionsClearRequested}
          onSuggestionSelected={this.onSuggestionSelected}
          getSuggestionValue={this.getSuggestionValue}
          renderSuggestion={this.renderSuggestion}
          inputProps={inputProps} />
      </td>
    );
  }
}

class TextInput extends React.Component {
  constructor(props) {
    super(props);
    if ('defaultValue' in this.props && this.props.defaultValue !== null) {
      this.state = {value: this.props.defaultValue};
    } else {
      this.state = {value: ''};      
    }
    this.handleChange = this.handleChange.bind(this);
  }
  
  handleChange(event) {
    if ('defaultValue' in this.props && Array.isArray(this.props.defaultValue)) {
      var nextValue = this.state.value.slice();
      nextValue[$(event.target).data('index')] = event.target.value;
      this.setState({value: nextValue});
    } else {
      this.setState({value: event.target.value});      
    }
  }
  
  render() {
    if (Array.isArray(this.state.value)) {
      var formInput = [];
      for (var i=0; i<this.state.value.length; i++) {
        if (i !== 0) {
          formInput.push(<br key={i + "_br"}/>);
        }
        formInput.push(<input type="text" key={i} data-index={i}
          name={this.props.data.name} maxLength={this.props.data.parameter}
          value={this.state.value[i]} onChange={this.handleChange}/>);
      }
    } else {
      var formInput = (<input type="text" 
        name={this.props.data.name} maxLength={this.props.data.parameter} 
        value={this.state.value} onChange={this.handleChange}/>)
    }
    return (
      <td>{formInput}</td>      
    );
  }
}
TextInput.propTypes = {
  data: React.PropTypes.shape({
    name: React.PropTypes.string.isRequired,
    parameter: React.PropTypes.number.isRequired,
  }),
  defaultValue: React.PropTypes.string
}

class Dropdown extends React.Component {
  constructor(props) {
    super(props);
    this.state = {value: 'default'};
    this.handleChange = this.handleChange.bind(this);
  }
  handleChange(event) {
    this.setState({value: event.target.value});
  }
  render() {
    return (
      <td>
      <select name={this.props.data.name}
        value={this.state.value} onChange={this.handleChange}>
        <option value="default">Select</option>
        {this.props.data.parameter.map((p, i) => {
          return (<option key={i} value={p[1]}>{p[0]}</option>);
        })}
      </select>
      </td>
    );
  }
}
Dropdown.propTypes = {
  data: React.PropTypes.shape({
    name: React.PropTypes.string.isRequried,
    parameter: React.PropTypes.arrayOf(
      tuple
    ).isRequired
  }).isRequired
}

class DateField extends React.Component {
  render() {
    return (
      <td>
        <input type="text" className="datepicker" id={this.props.data.name}
          name={this.props.data.name} value={this.props.data.value}/>
      </td>
    );
  }
}
DateField.propTypes = {
  data: React.PropTypes.shape({
    name: React.PropTypes.string.isRequired,
    value: React.PropTypes.string.isRequired
  }).isRequired
}

class Button extends React.Component {
  render() {
    return (
      <td>
        <button type="button" data-parameter={this.props.data.parameter} name={this.props.data.name}
          className="prettyBtn">{this.props.data.label}</button>
      </td>
    );
  }
}
Button.propTypes = {
  data: React.PropTypes.shape({
    parameter: React.PropTypes.string.isRequired,
    name: React.PropTypes.string.isRequired,
    label: React.PropTypes.string.isRequired
  }).isRequired
}

class SubmitButton extends React.Component {
  render() {
    return (
      <td>
      <button type="submit" value={this.props.data.parameter} name="state"
        className="submitBtn prettyBtn" style={{color: "darkred"}}>{this.props.data.label}</button>
      </td>
    );
  }
}
SubmitButton.propTypes = {
  data: React.PropTypes.shape({
    parameter: React.PropTypes.string.isRequired,
    label: React.PropTypes.string.isRequired
  }).isRequired
}

class ResetButton extends React.Component {
  render() {
    return (
      <td>
      <button type="button" id="search-reset" className="prettyBtn">
        Reset
      </button>
      </td>
    );
  }
}

class FormField extends React.Component {
  render() {
    switch(this.props.data.type) {
      case 'dropdown':
        return (<Dropdown data={this.props.data}/>);
        break;
      case 'text':
        if ('name' in this.props.data && this.props.data.name.length > 3 && this.props.data.name[2] === '.') {
          if ('defaultValue' in this.props) {
            return (<AutosuggestInput data={this.props.data} defaultValue={this.props.defaultValue}/>);
          }
          return (<AutosuggestInput data={this.props.data}/>);
        }
        if ('defaultValue' in this.props) {
          return (<TextInput data={this.props.data} defaultValue={this.props.defaultValue}/>);
        }
        return (<TextInput data={this.props.data}/>);
        break;
      case 'integer':
      case 'string':
        return (<td>{this.props.defaultValue}</td>);
        break;
      case 'hidden':
        return (<td><input type="hidden" value={this.props.defaultValue}/></td>);
        break;
      case 'date':
        return (<DateField data={this.props.data}/>);
        break;
      case 'button':
        if (this.props.data.name !== 'start' && this.props.data.name !== 'reset') {
          return (<Button data={this.props.data}/>);
        } else {
          console.log('error rendering');
          console.log(this.props.data);
          return (<td></td>);
        }
        break;
      default:
        console.log('error rendering');
        console.log(this.props.data);
        return (<td></td>);
    }
  }
}
FormField.propTypes = {
  data: React.PropTypes.shape({
    type: React.PropTypes.oneOf(['dropdown', 'text', 'integer', 'string', 'hidden', 'date', 'button']).isRequired,
    name: React.PropTypes.string,
  }).isRequired,
  defaultValue: React.PropTypes.any
}

class SearchForm extends React.Component {
  constructor(props) {
    super(props);
    this.state = {applayout: [], resultlayout: {}};
    this.handleSubmit = this.handleSubmit.bind(this);
  }
  handleSubmit(event) {
    event.preventDefault();
    var submission = $(event.target).serializeArray();
    submission.push({name: 'state', value: $(event.target).find('button[name=state]').val()});
    submission.push({name: 'appname', value: this.props.appName});
    
    $.ajax({
      url: this.props.url,
      data: submission,
      dataType: 'json',
      cache: false,
      success: function(data) {
        // console.log(data);
        this.setState({resultlayout: data});
      }.bind(this),
      error: function(xhr, status, err) {
        console.error(this.props.url, status, err.toString());
      }.bind(this)
    });
  }
  componentDidMount() {
    $.ajax({
      url: this.props.url,
      data: {
        state: this.props.appState,
        appname: this.props.appName
      },
      dataType: 'json', 
      cache: false,
      success: function(data) {
        this.setState({applayout: data.applayout});
      }.bind(this),
      error: function(xhr, status, err) {
        console.error(this.props.url, status, err.toString());
      }.bind(this)
    });
  }
  render() {
    var data = this.state.applayout.filter((cellLayout) => {
      return cellLayout.type !== 'button';
    });
    data.sort((a,b) => { 
      return (a.row-b.row !== 0 ? a.row-b.row : a.column-b.column); 
    });
    
    var rowCount = data.length > 0 ? data[0].row : 0;
    var cells = [];
    var rows = [];
    for (var i=0; i<data.length; i++) {
      //when the row changes push the current set of cells 
      //into a <tr> to `rows`, reset `cells`, and increment rowCount
      if ('row' in data[i] && data[i].row !== rowCount) {
        rows.push(<tr key={rowCount}>{cells}</tr>);
        cells = [];
        rowCount = data[i].row;
      }
      
      //in the case of buttons, the `label` property is used by the button
      //all other cases, though, `label` is displayed before the form field
      if ('label' in data[i] && data[i].type !== 'button') {
        var style = data[i].hasOwnProperty('style') ? data[i].style : {};
        cells.push (
          <td key={data[i].id + '_label'} style={style}>
            <label>{data[i].label}</label>
          </td>
        );        
      }
      
      cells.push(<FormField key={data[i].id + '_field'} data={data[i]}/>);

    }
    rows.push(<tr key={rowCount}>{cells}</tr>);
    cells = [];
    
    //force submit and reset buttons to be in their own row at the very end
    var submit = this.state.applayout.find((formItem) => { return formItem.name === 'start'; });
    var reset = this.state.applayout.find((formItem) => { return formItem.name === 'reset'; });
    if (submit) {
      cells.push(<SubmitButton key={submit.id + '_button'} data={submit}/>);
    } else if(data.length > 0) {
      console.log('error - no submit button specified, next state unknown');
    }
    if (reset) {
      cells.push(<Button key={reset.id + '_button'} data={reset}/>);
    } else {
      cells.push(<ResetButton key='reset'/>);
    }
    rows.push(<tr key={rowCount+1}>{cells}</tr>);
    
    var results = '';
    if (!$.isEmptyObject(this.state.resultlayout)) {
      results = (<ResultsForm data={this.state.resultlayout} url={this.props.url}/>);
    }
    
    return (
      <div>
        <form className="searchForm" onSubmit={this.handleSubmit}>
          <table><tbody>
          {rows}
          </tbody></table>
        </form>
        {results}
      </div>
    );
  }
}
SearchForm.propTypes = {
  url: React.PropTypes.string.isRequired,
  appState: React.PropTypes.oneOf(['start', 'review', 'update']).isRequired,
  appName: React.PropTypes.string.isRequired
}


class ResultsForm extends React.Component {
  constructor(props) {
    super(props);
    this.state = {data: this.props.data};
    this.handleSubmit = this.handleSubmit.bind(this);
  }
  //https://facebook.github.io/react/docs/react-component.html
  //when a component sets it's internal state based upon props it receives from the parent
  //the component NO LONGER re-renders whenever the props are changed by the parent,
  //instead only re-rendering whenever the internal state is changed. here we override that 
  //behavior by manually resetting state whenever the props are changed by the SearchForm
  componentWillReceiveProps(nextProps) {
    if (JSON.stringify(this.state.data.table) !== JSON.stringify(nextProps.data.table) || 
        JSON.stringify(this.state.data.applayout) !== JSON.stringify(nextProps.data.applayout)) {
      this.setState({data: nextProps.data});
    }
  }
  handleSubmit(event) {
    event.preventDefault();
    var rows = $(event.target).find('tr');
    //first row is header elements
    rows.splice(0,1);
    //last row is submit buttons
    rows.splice((rows.length-1), 1);
    
    //TODO: handle packaging up results
    var items=[];
    for (var i=0; i<rows.length; i++) {
      var row = {csid: $(rows[i]).data('csid'), cells: []};
      
      var cells = $(rows[i]).find('td');
      var itemValues = [];
      
      for (var j=0; j<cells.length; j++) {
        var isInputCell = false;
        var cellValues = [];

        var cellInputElements = $(cells[j]).find(':input');
        if (cellInputElements.length > 1) {
          isInputCell = true;
          cellValues = [];
          for (var k=0; k<cellInputElements.length; k++) {
            cellValues.push($(cellInputElements[k]).val());
          }
        } else if (cellInputElements.length === 1) {
          isInputCell = true;
          cellValues = $(cellInputElements[0]).val();
        } 
        
        if(isInputCell) {
          itemValues.push(cellValues);
        }
      }
      
      //don't add anything from subheader rows or rows without input elements
      if (itemValues.length > 0) {
        row.cells = itemValues;
        items.push(row);        
      }
    }

    var submission = {
      items: items,
      state: $(event.target).find('button[name=state]').val(),
      appname: this.state.data.appname,
      csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
    };
    // console.log(submission);

    $.post({
      url: this.props.url,
      data: submission,
      dataType: 'json',
      cache: false,
      success: function(data) {
        // console.log(data);
        this.setState({data: data});
      }.bind(this),
      error: function(xhr, status, err) {
        console.error(this.props.url, status, err.toString());
      }.bind(this)
    });
  }
  render() {
    var data = this.state.data;
    
    var header, rows, resultsText, submitButtons, error;
    if ('applayout' in data) {
      //exclude all buttons in applayout from the row layout
      var rowlayout = data.applayout.filter((cellLayout) => {
        return cellLayout.type !== 'button';
      });

      header = rowlayout.map((cell) => {
        return (<th key={cell.id}>{cell.label}</th>);
      });

      if ('table' in data) {
        var sections = data.table.map((section) => {
          var rows = section.items.map((item) => {
            // if ('csid' in item) {
            //   var unique = item.csid;
            var unique = Math.random();

            var cells = [];
            if (rowlayout.length > 0) {
              for (var i=0; i<rowlayout.length; i++) {
                cells.push(<FormField key={unique + '_' + rowlayout[i].id} data={rowlayout[i]} defaultValue={item.cells[i]}/>);
              }
            } else {
              for (var i=0; i<item.cells.length; i++) {
                cells.push(<FormField key={unique + '_' + item.cells[i]} data={{type: 'string'}} defaultValue={item.cells[i]}/>);
              }
            }
            return (<tr data-csid={item.csid} key={unique}>{cells}</tr>);
          });
          var unique = Math.random();
          var subheader = (<tr key={unique}><td colSpan={rowlayout.length}>{section.subheader}</td></tr>);
          rows.unshift(subheader);
          return rows
        });
        resultsText = (<p>{data.numberofitems} items listed.</p>);
      } 
      else if ('items' in data) {
        var sections = data.items.map((item) => {
          var unique = Math.random();

          var cells = [];
          if (rowlayout.length > 0) {
            for (var i=0; i<rowlayout.length; i++) {
              cells.push(<FormField key={unique + '_' + rowlayout[i].id} data={rowlayout[i]} defaultValue={item.cells[i]}/>);
            }
          } else {
            for (var i=0; i<item.cells.length; i++) {
              cells.push(<FormField key={unique + '_' + item.cells[i]} data={{type: 'string'}} defaultValue={item.cells[i]}/>);
            }
          }
          return (<tr data-csid={item.csid} key={unique}>{cells}</tr>);
        });
      }

      submitButtons = [];
      var submit = this.state.data.applayout.find((formItem) => { return formItem.name === 'review'; });
      var reset = this.state.data.applayout.find((formItem) => { return formItem.name === 'reset'; });
      if (submit) {
        submitButtons.push(<SubmitButton key={submit.id + '_button'} data={submit}/>);
      } else if(data.length > 0) {
        console.log('error - no submit button specified, next state unknown');
      }
      if (reset) {
        submitButtons.push(<Button key={reset.id + '_button'} data={reset}/>);
      } else {
        submitButtons.push(<ResetButton key='reset'/>);
      }
      submitButtons = (<table><tbody><tr>{submitButtons}</tr></tbody></table>);
    }

    if ('error' in data) {
      error = (<div className="error"><hr/>{data.error}</div>);
    }

    return (
      <div>
        {error}
        <form className="resultsForm" onSubmit={this.handleSubmit}>
        <table>
          <thead><tr>{header}</tr></thead>
          <tbody>{sections}</tbody>
        </table>
        <hr/>
        {resultsText}
        {submitButtons}
        </form>
      </div>
    )
  }
}

ResultsForm.propTypes = {
  data: React.PropTypes.shape({
    applayout: React.PropTypes.arrayOf(React.PropTypes.shape({
      id: React.PropTypes.number.isRequired,
      label: React.PropTypes.string.isRequired,
      name: React.PropTypes.string.isRequired,
      type: React.PropTypes.string.isRequired,
      column: React.PropTypes.string,
      row: React.PropTypes.string
    })).isRequired,
    appname: React.PropTypes.string.isRequired,
    table: React.PropTypes.arrayOf(React.PropTypes.shape({
      items: React.PropTypes.arrayOf(React.PropTypes.shape({
        csid: React.PropTypes.string.isRequired,
        cells: React.PropTypes.array.isRequired
      })),
      subheader: React.PropTypes.string,
      footer: React.PropTypes.string
    })),
    // items: React.PropTypes.arrayOf(React.PropTypes.shape({
    //   csid: React.PropTypes.string.isRequired,
    //   cells: React.PropTypes.array.isRequired,
    // })),
    numberOfItems: React.PropTypes.number
  }).isRequired,
  url: React.PropTypes.string.isRequired
}

var displayApp = function(appName) {
  ReactDOM.render(
    <SearchForm url="/toolbox/json/" appState='start' appName={appName}/>,
    document.getElementById('searchForm')
  ); 
}

export {displayApp};

// ReactDOM.render(
//   <ResultsForm />, document.getElementById('resultsForm')
// );
